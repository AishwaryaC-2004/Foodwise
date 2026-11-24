from restaurant.models import ProductionLog
from .models import NGORequirement, DonationMatch


def run_matching():


    requirements = NGORequirement.objects.all()

    for requirement in requirements:

        leftovers = ProductionLog.objects.filter(
            menu_item__item_name=requirement.food_item,
            leftover_quantity__gt=0
        ).order_by('-leftover_quantity')

        needed = requirement.quantity_required

        for leftover in leftovers:

            if needed <= 0:
                break

            available = leftover.leftover_quantity

            allocated = min(
                available,
                needed
            )

            existing = DonationMatch.objects.filter(
                ngo=requirement.ngo,
                production_log=leftover,
                status="Pending"
            )

            if existing.exists():
                continue
            DonationMatch.objects.create(
                ngo=requirement.ngo,
                production_log=leftover,
                allocated_quantity=allocated,
                status="Pending"
            )

            