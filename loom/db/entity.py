from sqlalchemy import Column, Index, Unicode, DateTime, func

from loom.db.util import Base, BigIntegerType


class Entity(Base):
    """ Type declarations for type declarations. """
    __tablename__ = 'entity'
    __table_args__ = (
        Index('ix_entity_subject', 'subject'),
        Index('ix_entity_schema', 'schema'),
        Index('ix_entity_source', 'source')
    )

    id = Column(BigIntegerType, primary_key=True)
    subject = Column(Unicode(1024))
    schema = Column(Unicode(255))
    source = Column(Unicode(255))
    created_at = Column(DateTime, default=func.now(), nullable=True)

    def __repr__(self):
        return '<Entity(%s,%s)>' % (self.subject, self.schema)
