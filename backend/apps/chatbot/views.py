import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message, KnowledgeEntry
from .serializers import ConversationSerializer, MessageSerializer, KnowledgeEntrySerializer
from apps.tickets.models import Ticket

# Try to import sentence-transformers; fall back to simple hashing if unavailable
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBED_AVAILABLE = True
except Exception:
    EMBED_AVAILABLE = False

import os
EMBED_MODEL = os.getenv('EMBEDDING_MODEL_NAME', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
if EMBED_AVAILABLE:
    embedder = SentenceTransformer(EMBED_MODEL)
else:
    # fallback embedder: simple char-based vectorization
    def simple_embed(text):
        v = [0]*32
        for i,c in enumerate(text):
            v[i%32] = (v[i%32] + ord(c)) % 256
        return v

KB_EMBEDDINGS = []
KB_ENTRIES = []

class CreateSessionView(APIView):
    def post(self, request):
        session_id = str(uuid.uuid4())
        conv = Conversation.objects.create(session_id=session_id)
        return Response({'session_id': session_id}, status=status.HTTP_201_CREATED)

class SendMessageView(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        text = request.data.get('text')
        if not session_id or not text:
            return Response({'detail': 'session_id and text required'}, status=status.HTTP_400_BAD_REQUEST)
        conv, _ = Conversation.objects.get_or_create(session_id=session_id)
        msg = Message.objects.create(conversation=conv, sender_type='user', text=text, is_bot=False)

        # embed
        if EMBED_AVAILABLE:
            q_emb = embedder.encode([text])[0]
            if len(KB_EMBEDDINGS) > 0:
                sims = np.inner(KB_EMBEDDINGS, q_emb)
                top_idx = int(np.argmax(sims))
                top_score = float(sims[top_idx])
                if top_score > 0.7:
                    kb = KB_ENTRIES[top_idx]
                    bot_text = f"Respuesta basada en KB: {kb.solution_text}"
                else:
                    bot_text = f"Respuesta generada (fallback): No tengo una KB relevante. Intentando ayudar: {text}"
            else:
                bot_text = f"Respuesta generada (fallback): No hay KB cargada. Intentando ayudar: {text}"
        else:
            # fallback simple matching
            bot_text = 'Respuesta simple: ' + (KB_ENTRIES[0].solution_text if KB_ENTRIES else f'No KB. Echo: {text}')

        bot_msg = Message.objects.create(conversation=conv, sender_type='bot', text=bot_text, is_bot=True)

        # if escalates, create ticket
        if 'agente' in text.lower() or 'hablar con agente' in text.lower():
            t = Ticket.objects.create(creador=None, asunto=f'Escalada desde chat {session_id}', prioridad=1.0)
            t.recibir_mensaje({'from':'user', 'text': text})

        return Response({'bot': bot_text}, status=status.HTTP_200_OK)

class ConversationDetailView(APIView):
    def get(self, request, session_id):
        try:
            conv = Conversation.objects.get(session_id=session_id)
        except Conversation.DoesNotExist:
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        ser = ConversationSerializer(conv)
        return Response(ser.data)

class FeedbackView(APIView):
    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        conv = None
        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                conv = None
        # create Feedback minimal
        from .models import Feedback
        fb = Feedback.objects.create(conversation=conv, rating=rating, comment=comment)
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)

class KBListCreateView(APIView):
    def get(self, request):
        kbs = KnowledgeEntry.objects.all()
        ser = KnowledgeEntrySerializer(kbs, many=True)
        return Response(ser.data)
    def post(self, request):
        ser = KnowledgeEntrySerializer(data=request.data)
        if ser.is_valid():
            kb = ser.save()
            # update in-memory KB index
            KB_ENTRIES.append(kb)
            vec = embedder.encode([kb.problem_description])[0]
            KB_EMBEDDINGS.append(vec)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class ReindexView(APIView):
    def post(self, request):
        global KB_EMBEDDINGS, KB_ENTRIES
        KB_EMBEDDINGS = []
        KB_ENTRIES = []
        for kb in KnowledgeEntry.objects.all():
            KB_ENTRIES.append(kb)
            if EMBED_AVAILABLE:
                vec = embedder.encode([kb.problem_description])[0]
            else:
                vec = simple_embed(kb.problem_description)
            KB_EMBEDDINGS.append(vec)
        return Response({'status': 'reindexed', 'count': len(KB_ENTRIES)})
