from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Custom permission: allow read access to anyone authenticated,
    but write access only to the author.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are GET, HEAD, OPTIONS → always allowed
        if request.method in SAFE_METHODS:
            return True

        # Write permissions only allowed to the author
        return obj.author == request.user
