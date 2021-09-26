from django.shortcuts import render, get_object_or_404

from django.http.response import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from .models import Message
from .serializers import MessageSerializer

from rest_framework.decorators import action
from itertools import chain


class MessagesViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def destroy(self, request, pk=None, **kwargs):
        """
        URL: 127.0.0.1:8000/api/messages/pk/
        Deletes one message that the user sent or received
        @param request: DELETE http request
        @param pk: message id
        @return: http response with the message that's deleted
        """
        try:
            pk = int(pk)
            user = User.objects.get(username=request.user)
            sent_messages = user.sent_messages.filter(pk=pk)
            recieved_messages = user.recieved_messages.filter(pk=pk)
            message_to_delete = list(chain(sent_messages, recieved_messages))
            if not len(message_to_delete):
                return Response({"Message to delete was not found"})
            message_to_delete[0].delete()
            return Response({"Deleted message successfully"})
        except ValueError:
            return HttpResponseNotFound("To delete a message provide a pk")

    def create(self, request, **kwargs):
        """
        Url:127.0.0.1:8000/api/messages/
        POST new message(the authorize user is the sender)
        @param request: POST http request
        @return:http response with the message that's created
        """
        msg_data = request.data
        current_user = request.user

        if current_user.username != msg_data['sender']:
            return HttpResponseForbidden("You can't send messages from other users!")
        msg_to = msg_data['reciever']
        reciever = User.objects.get(username=msg_to)
        if not reciever:
            return HttpResponseNotFound("Reciever user not found")

        new_message = Message(sender=current_user, reciever=reciever, subject=msg_data['subject'],
                              message=msg_data['message'], reciever_read_message=False)
        new_message.save()
        msg_serializer = MessageSerializer(new_message)
        return Response(msg_serializer.data)

    @action(detail=False, methods=['GET'])
    def newmessages(self, request, pk=None):
        """
        Url: 127.0.0.1:8000/api/messages/newmessages
        Get the messages the authorized user received and didn't read
        @param request:GET http request
        @return:returns http response with all the unread messages
        """
        user = User.objects.get(username=request.user)
        new_messages_query = user.recieved_messages.filter(reciever_read_message=False)
        if not len(new_messages_query):
            return Response({"No new messages"})

        new_messages = [MessageSerializer(message).data for message in new_messages_query]
        return Response(new_messages)

    @action(detail=False, methods=['PUT'])
    def nextmessage(self, request, pk=None):
        """
        Url: 127.0.0.1:8000/api/messages/nextmessage/
        Update the specific message to read.
        @param request: GET http request
        @param pk:message id
        @return:http response with the updated message
        """
        user = User.objects.get(username=request.user)
        messages_not_read = user.recieved_messages.filter(reciever_read_message=False)
        if not len(messages_not_read):
            return Response({"No unread messages"})
        new_message = messages_not_read[0]
        new_message.reciever_read_message = True
        new_message.save()
        msg_serializer = MessageSerializer(new_message)
        return Response(msg_serializer.data)

    def list(self, request, *args, **kwargs):
        """
            Url is: http://127.0.0.1/api/messages/
            get the list of all users' messages.
            @param request:GET http request
            @return: Response the list of messages for the currently authenticated user
        """
        user = User.objects.get(username=request.user)
        sent_messages = user.sent_messages.all()
        recieved_messages = user.recieved_messages.all()
        all_messages_query_set = list(chain(sent_messages, recieved_messages))

        all_messages_serializer = MessageSerializer(all_messages_query_set, many=True)
        return Response(all_messages_serializer.data)
