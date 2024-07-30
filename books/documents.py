from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Book


@registry.register_document
class BookDocument(Document):
    title = fields.TextField(
        attr='title',
        fields={
            'raw': fields.TextField(),
            'suggest': fields.CompletionField(),
        }
    )
    description = fields.TextField(
        attr='description',
        fields={
            'raw': fields.TextField(),
        }
    )
    author = fields.ObjectField(
        attr='author',
        properties={
            'id': fields.IntegerField(),
            'title': fields.TextField(
                attr='title',
                fields={
                    'raw': fields.KeywordField(),
                }
            )
        }
    )
    genre = fields.ObjectField(
        attr='genre',
        properties={
            'id': fields.IntegerField(),
            'title': fields.TextField(
                attr='title',
                fields={
                    'raw': fields.KeywordField(),
                }
            )
        }
    )


    class Index:
        name = 'books'

    class Django:
        model = Book
