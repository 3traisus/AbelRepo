from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.views import APIView
import json
from rest_framework.response import Response
from rest_framework import status, viewsets
from .serializers import ProductSerializer, QuestionSerializer
from .models import Product, Question
from openai import OpenAI
from django.conf import settings

# Create your views here.
#Metodo para extraer los datos del formato Json y poder agregarlos a la base de datos
class ExtraProductAPIView(APIView):
    def get(self, request, *args, **kwargs):

        with open('api/example2.json', 'r', encoding='utf-8') as file:
            date = json.load(file)

            #item_date = date.get('item', {})
            #question_date = date.get('question', [])

            #print(datos)
            datos = Product.objects.get_or_create(
                id_item=date['id_item'],
                defaults={
                    'title': date['title'],
                    'price': date['price'],
                    'currency_id': date['currency_id'],
                    'available_quantity': date['available_quantity'],
                    'sold_quantity': date['sold_quantity'],
                    'condition': date['condition'],
                    'attributes': date['attributes'],
                }
            )
            '''
            for question_dates in question_date:
                question, created = Question.objects.get_or_create(
                    question_id=question_dates['question_id'],
                    defaults={
                        'item': datos,
                        'text': question_dates['text'],
                        'status': question_dates['status'],
                        'answer': question_dates['answer', ''],
                        'date_created': question_dates['date_created'],
                    }
                )
            '''
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            product_attributes = f"Titulo: {date['title']}\nPrecio: {date['price']} {date['currency_id']}\nAtributos: {date['attributes']}"
            for question in date['questions']:
                prompt = f"\n\nLa pregunta es:{question.text}\nRespuesta:"

                response = client.chat.completions.create(
                    model="",
                    messages=[
                        {"role": "system", "content": "Eres un asistente que responde mensajes relacionados a la venta de productos en linea"},
                        {"role": "user", "content": product_attributes},
                        {"role": "assistant", "content": "De acuerdo a las caracteristicas que me brindaste cual es tu pregunta? "},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=250,
                    temperature=0.2,
                )
                answer = response.choices[0].message.content
                # answer = response.choices[0].text.split()
                datos[question]['answer'] = answer
                datos[question]['status'] = 'ANSWERED'

                serializer = ProductSerializer(datos)
                #serializers = QuestionSerializer(question, many=True)

            return Response(serializer.data, status=status.HTTP_201_CREATED), #Response(serializers.data, status=status.HTTP_200_OK)

#Clase y metodo para listar los productos obtenidos del formato Json
class ProductListView(APIView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    product_data = ''
    with open('api/example2.json', 'r', encoding='utf-8') as file:
        product_data = json.load(file)
    @action(detail=True, methods=['post'], url_path='question')
    def question(self, request, pk=None):
        prod = self.get_object()
        question_text = request.data.get('question_text')

        question_comparation = Question.objects.filter(item__question=prod, text__icontains=question_text).first()
        if question_comparation:
            if question_comparation.answer:
                return Response({'answer': question_comparation.answer}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'message': 'La pregunta esta siendo procesada'})

        question = Question.objects.create(
            id_item=f"{prod.item_id}-{len(prod.question_text.all()) + 1}",
            item=prod,
            text=question_text,
            status='PENDING',
        )

        product_attributes = f"Titulo: {prod.title}\nPrecio: {prod.price} {prod.currency_id}\nAtributos: {prod.attributes}"
        prompt = f"\n\nLa pregunta es:{question.text}\nRespuesta:"

        client = OpenAI

        assitent = client.beta.assistants.create(
            name='Swipbot',
            model="",
            instructions='',
            tools=[{"type": "code_interpreter"},{"type": "file_search"}],

        )
        api_key = settings.OPENAI_API_KEY
        response = client.chat.completions.create(
            model="",
            messages=[
                {"role": "system", "content": "Eres un asistente que responde mensajes relacionados a la venta de productos en linea"},
                {"role": "user", "content": product_attributes},
                {"role": "assistant", "content": "De acuerdo a las caracteristicas que me brindaste cual es tu pregunta? "},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.2,
        )
        answer = response.choices[0].message.content
        #answer = response.choices[0].text.split()
        question.answer = answer
        question.status = 'ANSWERED'
        question.save()

        return Response({'answer': answer})