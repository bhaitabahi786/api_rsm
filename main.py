from typing import Union
from typing import Annotated, List, Text
from fastapi import FastAPI,Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
import uuid
from sqlalchemy.sql import text 
from sqlalchemy import desc
import models as mm
from fastapi.middleware.cors import CORSMiddleware

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

# CORS Policy Change according to URL

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create table and db
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Create product entry
@app.post("/product/", response_model=mm.productPublic)
def create_product(product: mm.productCreate, session: SessionDep):
    db_product = mm.Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

# get Product entry
@app.get("/products/", response_model=List[mm.productPublic])
def get_product(limit: int, session: SessionDep):
    products = session.exec(select(mm.Product).limit(limit)).all()
    
    return products

@app.get("/All_Stocks/")
def allStocks(session: SessionDep):
    result = session.execute(text(
        """
        SELECT name, 
               SUM(purchase_qty) AS total_purchase, 
               SUM(sale_qty) AS total_sale 
        FROM Product 
        GROUP BY name
        """)
    ).fetchall()

    return [{"product_name": row[0], "total_purchase": row[1], "total_sale": row[2]} for row in result]

# sales Table entries 

@app.post("/sales/", response_model=mm.salesDetailPublic)
def create_sale(sale: mm.salesDetailsCreate, session: Session = Depends(get_session)):
    # Convert sale details (excluding items)
    sale_data = mm.salesDetails(
        date=sale.date,
        billNo=sale.billNo,
        CName=sale.CName,
        Phone=sale.Phone,
        Address=sale.Address,
        sellerName=sale.sellerName,
        totalAmount=sale.totalAmount,
        amountReceived=sale.amountReceived,
        expectedDate= sale.expectedDate

    )

    # Convert Sales Items properly
    sale_data.items = [mm.salesItems(**item.dict()) for item in sale.items]

    # Now adding entry in product table
    for item in sale.items:
        
        product_item = mm.Product(
            name= item.product_name,
            sale_qty= item.qty,
            salesPrice= item.rate,
            pDate= sale.date
        )

        session.add(product_item)

    # creating Advance balance records
    adv_data = mm.Payment(
        date= sale.date,
        billNo= sale.billNo,
        CName=sale.CName,
        Phone=sale.Phone,
        Address=sale.Address,
        totalAmount= sale.totalAmount
    )

    adv_data.advAmount = [mm.paymentDetails(
        receivedDate= sale.date,
        amount= sale.amountReceived
    )]

    session.add(adv_data)

    session.add(sale_data)
    session.commit()
    session.refresh(sale_data)
    
    return sale_data

# --- get all bill no ---

@app.get("/billNo/")
def bill_No(session: SessionDep):
    billno = session.exec(select(mm.salesDetails.billNo).order_by(desc(mm.salesDetails.billNo))).first()
    return billno

# ---- get Bill data ----

@app.get("/sales/{bill_no}/", response_model=mm.salesDetailPublic)
def get_sale_by_bill_no(bill_no: str, session: SessionDep):
    sale = session.exec(select(mm.salesDetails).where(mm.salesDetails.billNo == bill_no)).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

# ---- Purchase entry create

@app.post("/purchase/", response_model=mm.purchaseDetailPublic)
def create_purchase(purchase: mm.purchaseDetailsCreate, session: SessionDep):
    purchase_data = mm.purchaseDetails(
        date=purchase.date,
        billNo=purchase.billNo,
        gstNo=purchase.gstNo,
        PName=purchase.PName,
        Phone= purchase.Phone,
        Address= purchase.Address
    )

    # createing purchaseItem table entry
    purchase_data.items = [mm.purchaseItems(**item.dict()) for item in purchase.items]

    # Now adding entry in product table
    for item in purchase.items:
        
        product_item = mm.Product(
            name= item.product_name,
            purchase_qty= item.qty,
            purchasePrice= item.rate,
            pDate= purchase.date
        )

        session.add(product_item)

    # save in purchase and item table
    session.add(purchase_data)
    session.commit()
    session.refresh(purchase_data)
    
    return purchase_data


@app.get("/Payments/", response_model=List[mm.paymentPublic])
def PaymentRecords(limit: int, session: SessionDep):
    records = session.exec(select(mm.Payment).limit(limit)).all()
    return records

@app.post("/pay_update/", response_model=mm.paymentDetailsPublic)
def pay_update(payup: mm.paymentDetailsUpdate, session: SessionDep):
    pay_data = mm.paymentDetails(
        pay_id= payup.pay_id,
        receivedDate= payup.receivedDate,
        amount= payup.amount,
        totalPayReceived= payup.totalPayReceived
    )

    session.add(pay_data)
    session.commit()
    session.refresh(pay_data)
    
    return pay_data

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}