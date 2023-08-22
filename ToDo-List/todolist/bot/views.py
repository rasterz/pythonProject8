from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from todolist.bot.models import TgUser
from todolist.bot.serializers import TgUserSerializer
from todolist.bot.tg.client import TgClient


class VerificationView(GenericAPIView):
    model = TgUser
    permission_classes = [IsAuthenticated]
    serializer_class = TgUserSerializer

    def patch(self, request: Request, *args, **kwargs):
        s: TgUserSerializer = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        s.tg_user.user = request.user
        s.tg_user.save()

        TgClient().send_message(s.tg_user.chat_id, 'verification has been complited')
        return Response(self.get_serializer(s.tg_user).data)
