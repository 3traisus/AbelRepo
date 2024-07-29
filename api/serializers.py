from rest_framework import serializers
from .models import Product, Question



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        #['id_item', 'id_question', 'question', 'title', 'price']