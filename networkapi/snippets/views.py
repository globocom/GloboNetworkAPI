from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        data = {'success': 'List All Success'}
        return Response(data)

    elif request.method == 'POST':
        data = {'success': 'Post Data Success'}
        return Response(data, status=status.HTTP_201_CREATED)
