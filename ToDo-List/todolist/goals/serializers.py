from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from todolist.core.models import User
from todolist.core.serializers import ProfileSerializer
from todolist.goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')
        fields = '__all__'


class GoalCategorySerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


class GoalCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

        def validate_category(self, value: GoalCategory):
            if value.is_deleted:
                raise serializers.ValidationError('not allowed in deleted category')

            if value.user != self.context['request'].user:
                raise serializers.ValidationError('not owner of category')

            return value


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory):
        if value.user != self.context['request'].user:
            raise PermissionDenied
        return value


class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_goal(self, value):
        if value.status == Goal.Status.archived:
            raise serializers.ValidationError('Goal not found')
        user = self.context['request'].user
        if not BoardParticipant.objects.filter(
            board=value.category.board_id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
            user_id=user.id
        ).exists():
            raise serializers.PermissionDenied('You do not have permission to create a comment for this goal.')
        return value

    class Meta:
        model = GoalComment
        fields = ['goal', 'text', 'user']
        read_only_fields = ['user', 'created', 'updated']


class CommentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_comment(self, value: GoalComment):
        if value.user != self.context['request'].user:
            raise PermissionDenied
        return value


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board', 'is_deleted')

    def update(self, instance: Board, validated_data: dict):
        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance) \
                .exclude(user=self.context['request'].user) \
                .delete()
            BoardParticipant.objects.bulk_create([
                BoardParticipant(
                    user=participant['user'],
                    role=participant['role'],
                    board=instance
                )
                for participant in validated_data.get('participants', [])
            ])

            if title := validated_data.get('title'):
                instance.title = title
                instance.save(update_fields=('title',))

        return instance
