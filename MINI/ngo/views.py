from django.shortcuts import render, redirect
from .models import NGO
from .services import run_matching
from .models import DonationMatch
from .models import NGORequirement
from .models import DonationMatch

def ngo_login(request):

    if request.method == "POST":

        ngo_id = request.POST.get("ngo_id")

        try:

            ngo = NGO.objects.get(
                ngo_id=ngo_id
            )

            request.session["ngo_id"] = ngo.id

            return redirect(
                "ngo_dashboard"
            )

        except NGO.DoesNotExist:

            return render(
                request,
                "ngo/login.html",
                {
                    "error": "Invalid NGO ID"
                }
            )

    return render(
        request,
        "ngo/login.html"
    )


def ngo_dashboard(request):

    ngo_id = request.session.get(
        "ngo_id"
    )

    if not ngo_id:
        return redirect("ngo_login")

    ngo = NGO.objects.get(
        id=ngo_id
    )

    requirements = ngo.ngorequirement_set.all()
    matches = DonationMatch.objects.filter(
        ngo=ngo
    )
    return render(
        request,
        "ngo/dashboard.html",
        {
            "ngo": ngo,
            "requirements": requirements,
            "matches": matches
        }
    )
def run_matching_view(request):

    ngo_id = request.session.get("ngo_id")

    if not ngo_id:
        return redirect("ngo_login")

    ngo = NGO.objects.get(id=ngo_id)

    matches = DonationMatch.objects.filter(
        ngo=ngo
    )

    return render(
        request,
        "ngo/matches.html",
        {
            "matches": matches,
            "ngo": ngo
        }
    )
def requirements(request):

    ngo_id = request.session.get(
        "ngo_id"
    )

    if not ngo_id:
        return redirect("ngo_login")

    ngo = NGO.objects.get(
        id=ngo_id
    )

    if request.method == "POST":

        NGORequirement.objects.create(
            ngo=ngo,
            food_item=request.POST["food_item"],
            quantity_required=request.POST["quantity"]
        )

    requirements = NGORequirement.objects.filter(
        ngo=ngo
    )

    return render(
        request,
        "ngo/requirements.html",
        {
            "ngo": ngo,
            "requirements": requirements
        }
    )
def accept_match(request, match_id):

    match = DonationMatch.objects.get(
        id=match_id
    )

    if match.status == "Pending":

        production_log = match.production_log

        production_log.leftover_quantity -= (
            match.allocated_quantity
        )

        if production_log.leftover_quantity < 0:
            production_log.leftover_quantity = 0

        production_log.save()

        requirement = NGORequirement.objects.get(
            ngo=match.ngo,
            food_item=production_log.menu_item.item_name
        )

        requirement.quantity_required -= (
            match.allocated_quantity
        )

        if requirement.quantity_required < 0:
            requirement.quantity_required = 0

        requirement.save()

        match.status = "Accepted"
        match.save()

    return redirect("run_matching")
def reject_match(request, match_id):

    match = DonationMatch.objects.get(
        id=match_id
    )

    match.status = "Rejected"
    match.save()

    return redirect(
        "run_matching"
    )
def generate_matches(request):

    run_matching()

    return redirect("run_matching")