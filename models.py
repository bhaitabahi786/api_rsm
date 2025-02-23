from sqlmodel import Field, Session, SQLModel, create_engine, select,Relationship
import uuid
from datetime import date
from typing import Optional, List

# Product Stock table

class productBase(SQLModel):
    name: str = Field(index=True)
    sale_qty: int | None = None
    purchase_qty: int | None = None
    salesPrice: float | None = None
    purchasePrice: float | None = None
    pDate: date 

class Product(productBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class productPublic(productBase):
    id: uuid.UUID

class productCreate(productBase):
    pass

# ---- Clients record table 

class clientBase(SQLModel):
    name: str = Field(index=True)
    phone: str = Field(index=True)
    address: str = Field(index=True)

class Clients(clientBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class clientPublic(clientBase):
    id: uuid.UUID

class clientCreate(clientBase):
    pass

# ---- Bill Payment records ----

class paymentBase(SQLModel):
    date: date
    billNo: str
    CName: str
    Phone: str
    Address: str
    totalAmount: float 

class Payment(paymentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # payment details against bill
    advAmount: List["paymentDetails"] = Relationship(back_populates="billAmount")

# payment details to keep list of payment received records

class paymentDetailsBase(SQLModel):
    receivedDate: date | None = None
    amount: float | None = None
    totalPayReceived: bool | None = None

class paymentDetails(paymentDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    pay_id: uuid.UUID = Field(foreign_key="payment.id")
    # payment relationship
    billAmount: Optional[Payment] = Relationship(back_populates="advAmount")

class paymentDetailsPublic(paymentDetailsBase):
    id: uuid.UUID

class paymentDetailsCreate(paymentDetailsBase):
    pass

class paymentPublic(paymentBase):
    id: uuid.UUID
    advAmount: List[paymentDetailsPublic]

class paymentCreate(paymentBase):
    advAmount: List[paymentDetailsCreate]

# ---- payment update for adding payments received for particular bill no ----
class paymentDetailsUpdate(paymentDetailsBase):
    pay_id: uuid.UUID 


# ---- Sales record table

class salesDetailsBase(SQLModel):
    date: date
    billNo: str = Field(index=True, unique=True)
    CName: str 
    Phone: str 
    Address: str 
    sellerName: str | None = None
    totalAmount: float 
    amountReceived: float | None = None
    expectedDate: date | None = None

class salesDetails(salesDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # One-to-Many Relationship
    items: List["salesItems"] = Relationship(back_populates="sale")
    
# --- SalesItems (Child Table) ---

class salesItemBase(SQLModel):
    product_name: str
    qty: float
    rate: float
    amount: float

class salesItems(salesItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    sale_id: uuid.UUID = Field(foreign_key="salesdetails.id")
    # Relationship back to SalesDetails
    sale: Optional[salesDetails] = Relationship(back_populates="items")

# ---- Sales Table usages ----

class salesItemPublic(salesItemBase):
    id: uuid.UUID

class salesItemCreate(salesItemBase):
    pass

class salesDetailPublic(salesDetailsBase):
    id: uuid.UUID
    items: List[salesItemPublic]

class salesDetailsCreate(salesDetailsBase):
    items: List[salesItemCreate]

# ----- Purchase details -----

class purchaseDetailsBase(SQLModel):
    date: date
    billNo: str = Field(index=True)
    gstNo: str 
    PName: str 
    Phone: str 
    Address: str

class purchaseDetails(purchaseDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # One-to-Many Relationship
    items: List["purchaseItems"] = Relationship(back_populates="purchase")
    
# --- purchaseItems ---

class purchaseItemBase(SQLModel):
    product_name: str
    qty: float
    rate: float
    amount: float

class purchaseItems(purchaseItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    purchase_id: uuid.UUID = Field(foreign_key="purchasedetails.id")
    # Relationship back to purchaseDetails
    purchase: Optional[purchaseDetails] = Relationship(back_populates="items")

# ---- purchase Table usages ----

class purchaseItemPublic(purchaseItemBase):
    id: uuid.UUID

class purchaseItemCreate(purchaseItemBase):
    pass

class purchaseDetailPublic(purchaseDetailsBase):
    id: uuid.UUID
    items: List[purchaseItemPublic]

class purchaseDetailsCreate(purchaseDetailsBase):
    items: List[purchaseItemCreate]

# ----- Expenses Table

class expenseBase(SQLModel):
    date: date 
    expName: str = Field(index=True)
    description: str | None = None
    doneBy: str | None = None
    amount: float 

class expenses(expenseBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class expensePublic(expenseBase):
    id: uuid.UUID

class expenseCreate(expenseBase):
    pass





