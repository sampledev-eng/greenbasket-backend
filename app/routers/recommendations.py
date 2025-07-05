from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, auth, dependencies, recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/", response_model=list[models.Product])
def get_recommendations(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(auth.get_current_user),
    limit: int = 5,
):
    return recommendations.get_recommendations(db, current_user.id, limit)
