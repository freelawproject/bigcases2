from rest_framework import serializers


class RecapDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    description = serializers.CharField()
    filepath_ia = serializers.URLField()
    absolute_url = serializers.CharField()
    pacer_doc_id = serializers.CharField()
    document_number = serializers.CharField()
    attachment_number = serializers.CharField(allow_null=True)


class WebhookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date_filed = serializers.DateField()
    description = serializers.CharField()
    date_created = serializers.DateTimeField()
    entry_number = serializers.IntegerField()
    date_modified = serializers.DateTimeField()
    recap_documents = RecapDocumentSerializer(many=True)
    pacer_sequence_number = serializers.IntegerField()
    recap_sequence_number = serializers.CharField()
