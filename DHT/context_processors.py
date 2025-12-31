def get_user_role(request):
    if not request.user.is_authenticated:
        return {'role': None}
        
    role = "Utilisateur"
    if request.user.is_superuser:
        role = "Administrateur"
    elif request.user.groups.filter(name='Manager').exists():
        role = "Manager"
    elif request.user.groups.filter(name='Chief').exists():
        role = "Chef"
    elif request.user.groups.filter(name='Operator').exists():
        role = "Opérateur"
        
    return {'role': role}
