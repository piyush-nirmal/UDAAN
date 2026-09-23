from blood_request.models import SharedNote

def shared_notes_processor(request):
    """
    Provides a tree of SharedNotes for the portal sidebar (Wiki feature).
    Only includes root notes (those without a parent) that the user can access.
    The template will handle recursive rendering of children.
    """
    if not request.user.is_authenticated:
        return {'shared_notes_tree': []}
        
    user = request.user
    
    # Base filter: root notes (no parent) where user is owner, explicitly shared, or in a shared team
    root_notes = SharedNote.objects.filter(parent_note__isnull=True).filter(
        id__in=SharedNote.objects.filter(owner=user).values_list('id', flat=True).union(
            SharedNote.objects.filter(shared_with_users=user).values_list('id', flat=True),
            SharedNote.objects.filter(shared_with_teams__in=user.teams.all()).values_list('id', flat=True)
        )
    ).distinct().order_by('title')
    
    return {'shared_notes_tree': root_notes}
