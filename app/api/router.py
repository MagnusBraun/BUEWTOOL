from fastapi import APIRouter

from app.api.v1 import dokumente, kuep, lists, objects_update, projekte, upload, validate, vlp

api_router = APIRouter()
api_router.include_router(upload.router)
api_router.include_router(projekte.router)
api_router.include_router(kuep.router)
api_router.include_router(vlp.router)
api_router.include_router(validate.router)
api_router.include_router(dokumente.router)
api_router.include_router(lists.router)
api_router.include_router(objects_update.router)
