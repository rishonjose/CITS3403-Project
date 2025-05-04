from . import db

class BillEntry(db.Model):
    __tablename__ = 'bill_entries'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, nullable=False)    # link to your auth system later
    category      = db.Column(db.String(20), nullable=False) # e.g. 'Water', 'Electricity'
    units         = db.Column(db.Float,   nullable=False)    # numeric consumption
    cost_per_unit = db.Column(db.Float,   nullable=False)    # price per unit
    start_date    = db.Column(db.Date,    nullable=False)
    end_date      = db.Column(db.Date,    nullable=False)
    created_at    = db.Column(
                      db.DateTime,
                      server_default=db.func.now(),
                      nullable=False
                   )

    def __repr__(self):
        return (
            f"<BillEntry id={self.id!r} "
            f"category={self.category!r} "
            f"units={self.units!r} "
            f"cost_per_unit={self.cost_per_unit!r} "
            f"period={self.start_date}–{self.end_date}>"
        )
