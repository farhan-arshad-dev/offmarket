from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Ad


@registry.register_document
class AdDocument(Document):
    category = fields.ObjectField(properties={'id': fields.IntegerField(), 'name': fields.TextField()})
    neighbourhood = fields.ObjectField(properties={'id': fields.IntegerField(), 'name': fields.TextField(),
                                                   'city_id': fields.IntegerField()})

    class Index:
        name = 'ads'

    class Django:
        model = Ad
        fields = ['id', 'title', 'description', 'price', 'created_at']
