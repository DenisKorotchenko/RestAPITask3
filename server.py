from fastapi import FastAPI, HTTPException
import typing
from pydantic import BaseModel
from database import *
from random import shuffle
import uvicorn


app = FastAPI(title="Raffle")


class InputPromo(BaseModel):
    name: str
    description: typing.Optional[str]


class SmallPromo(InputPromo):
    id: int


class InputPrize(BaseModel):
    description: str


class Prize(InputPrize):
    id: int


class InputParticipant(BaseModel):
    name: str


class Participant(InputParticipant):
    id: int


class FullPromo(SmallPromo):
    prizes: typing.List[Prize]
    participants: typing.List[Participant]


class RaffleResult(BaseModel):
    winner: Participant
    prize: Prize


@app.post(
    "/promo",
    status_code=201
)
async def post_promo(promo: InputPromo):
    query = PromoDB.create(name=promo.name, description=promo.description)
    return query.__data__["id"]


@app.get(
    "/promo",
    response_model=typing.List[SmallPromo],
    status_code=200
)
async def get_all_promos():
    query = PromoDB.select()
    promos = []
    for promo in query.dicts().execute():
        promos.append(SmallPromo(id=promo["id"], name=promo["name"], description=promo["description"]))
    return promos


@app.get(
    "/promo/{id}",
    response_model=FullPromo,
    status_code=200
)
async def get_promo(id: int):
    try:
        promo = PromoDB.get(PromoDB.id == id)
    except DoesNotExist:
        raise HTTPException(status_code=404)

    participants = []
    query_participants = ParticipantDB.select().where(ParticipantDB.promo_id == id)
    for participant in query_participants.dicts().execute():
        participants.append(Participant(id=participant["id"], name=participant["name"]))

    prizes = []
    query_prizes = PrizeDB.select().where(PrizeDB.promo_id == id)
    for prize in query_prizes.dicts().execute():
        prizes.append(Prize(id=prize["id"], description=prize["description"]))
    output_promo = FullPromo(id=promo.id, name=promo.name, description=promo.description,
                             prizes=prizes,
                             participants=participants)
    return output_promo


@app.put(
    "/promo/{id}",
    status_code=204
)
async def change_promo(id: int, promo: InputPromo):
    promo = PromoDB(name=promo.name, description=promo.description)
    promo.id = id
    promo.save()
    return


@app.delete(
    "/promo/{id}",
    status_code=204
)
async def delete_promo(id: int):
    try:
        promo = PromoDB.get(PromoDB.id == id)
    except DoesNotExist:
        raise HTTPException(status_code=404)
    promo.delete_instance()
    return


@app.post(
    "/promo/{id}/participant",
    status_code=201
)
async def add_participant(id: int, participant: InputParticipant):
    query = ParticipantDB.create(name=participant.name, promo_id=id)
    return query.__data__["id"]


@app.delete(
    "/promo/{promo_id}/participant/{participant_id}",
    status_code=204
)
async def delete_participant(promo_id: int, participant_id: int):
    participant = ParticipantDB.get(ParticipantDB.id == participant_id and ParticipantDB.promo_id == promo_id)
    participant.delete_instance()
    return


@app.post(
    "/promo/{id}/prize",
    status_code=201
)
async def add_prize(id: int, prize: InputPrize):
    query = PrizeDB.create(description=prize.description, promo_id=id)
    return query.__data__["id"]


@app.delete(
    "/promo/{promo_id}/prize/{prize_id}",
    status_code=204
)
async def delete_prize(promo_id: int, prize_id: int):
    prize = PrizeDB.get(PrizeDB.id == prize_id and PrizeDB.promo_id == promo_id)
    prize.delete_instance()
    return


@app.post(
    "/promo/{id}/raffle",
    response_model=typing.List[RaffleResult],
    status_code=200
)
async def raffle(id: int):
    participants = []
    query_participants = ParticipantDB.select().where(ParticipantDB.promo_id == id)
    for participant in query_participants.dicts().execute():
        participants.append(Participant(id=participant["id"], name=participant["name"]))

    prizes = []
    query_prizes = PrizeDB.select().where(PrizeDB.promo_id == id)
    for prize in query_prizes.dicts().execute():
        prizes.append(Prize(id=prize["id"], description=prize["description"]))

    if len(participants) != len(prizes):
        raise HTTPException(status_code=409)

    shuffle(participants)
    shuffle(prizes)

    result = []
    for participant, prize in zip(participants, prizes):
        result.append(RaffleResult(winner=participant, prize=prize))

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
