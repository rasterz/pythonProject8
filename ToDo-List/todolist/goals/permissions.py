from rest_framework import permissions
from todolist.goals.models import BoardParticipant, Board, GoalCategory, Goal, GoalComment


class BoardPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Board):
        _filters: dict = {'user_id': request.user.id, 'board_id': obj.id}

        if request.method not in permissions.SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCategoryPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: GoalCategory):
        _filters: dict = {'user_id': request.user.id, 'board': obj.board_id}

        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Goal):
        _filters: dict = {'user_id': request.user.id, 'board': obj.category.board_id}

        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCommentsPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: GoalComment):
        return request.method in permissions.SAFE_METHODS or obj.user_id == request.user.id
