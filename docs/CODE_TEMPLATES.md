# 🛠️ PROJEKTO KŪRIMO ŠABLONAI

> Šis failas turi copy-paste šablonus dažnai naudojamiems komponentams.
> Naudok juos kaip pradžios tašką kuriant naujus failus.

---

## 📋 TURINYS

1. [Python - FastAPI Endpoint](#python---fastapi-endpoint)
2. [Python - SQLAlchemy Model](#python---sqlalchemy-model)
3. [Python - Pydantic Schema](#python---pydantic-schema)
4. [Python - Service](#python---service)
5. [TypeScript - React Component](#typescript---react-component)
6. [TypeScript - API Hook](#typescript---api-hook)
7. [TypeScript - Zustand Store](#typescript---zustand-store)
8. [SQL - Nauja lentelė](#sql---nauja-lentelė)

---

## Python - FastAPI Endpoint

```python
# backend/routers/example.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from schemas.example import ExampleCreate, ExampleRead, ExampleUpdate
from services.example_service import ExampleService

router = APIRouter(prefix="/examples", tags=["Examples"])


@router.get("/", response_model=List[ExampleRead])
async def get_all_examples(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[ExampleRead]:
    """
    Gauti visus įrašus.
    """
    service = ExampleService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{example_id}", response_model=ExampleRead)
async def get_example(
    example_id: int,
    db: AsyncSession = Depends(get_db)
) -> ExampleRead:
    """
    Gauti vieną įrašą pagal ID.
    """
    service = ExampleService(db)
    result = await service.get_by_id(example_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Įrašas nerastas"
        )
    return result


@router.post("/", response_model=ExampleRead, status_code=status.HTTP_201_CREATED)
async def create_example(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db)
) -> ExampleRead:
    """
    Sukurti naują įrašą.
    """
    service = ExampleService(db)
    return await service.create(data)


@router.put("/{example_id}", response_model=ExampleRead)
async def update_example(
    example_id: int,
    data: ExampleUpdate,
    db: AsyncSession = Depends(get_db)
) -> ExampleRead:
    """
    Atnaujinti esamą įrašą.
    """
    service = ExampleService(db)
    result = await service.update(example_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Įrašas nerastas"
        )
    return result


@router.delete("/{example_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_example(
    example_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Ištrinti įrašą.
    """
    service = ExampleService(db)
    success = await service.delete(example_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Įrašas nerastas"
        )
```

---

## Python - SQLAlchemy Model

```python
# backend/models/example.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship

from database import Base


class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    value = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

    # Foreign Key
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Parent", back_populates="examples")
    children = relationship("Child", back_populates="example", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Example(id={self.id}, name='{self.name}')>"
```

---

## Python - Pydantic Schema

```python
# backend/schemas/example.py

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ExampleBase(BaseModel):
    """Bazinė schema su bendrais laukais."""
    name: str = Field(..., min_length=1, max_length=100, description="Pavadinimas")
    description: Optional[str] = Field(None, max_length=1000, description="Aprašymas")
    value: float = Field(default=0.0, ge=0, description="Reikšmė")
    is_active: bool = Field(default=True, description="Ar aktyvus")


class ExampleCreate(ExampleBase):
    """Schema naujo įrašo kūrimui."""
    parent_id: Optional[int] = Field(None, description="Tėvinio įrašo ID")


class ExampleUpdate(BaseModel):
    """Schema įrašo atnaujinimui (visi laukai optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    value: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


class ExampleRead(ExampleBase):
    """Schema skaitymo operacijoms."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ExampleWithChildren(ExampleRead):
    """Schema su vaikiniais įrašais."""
    children: List["ChildRead"] = []
```

---

## Python - Service

```python
# backend/services/example_service.py

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.example import Example
from schemas.example import ExampleCreate, ExampleUpdate


class ExampleService:
    """Servisas Example CRUD operacijoms."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Example]:
        """Gauti visus įrašus su paginacija."""
        query = select(Example).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, example_id: int) -> Optional[Example]:
        """Gauti įrašą pagal ID."""
        query = select(Example).where(Example.id == example_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, data: ExampleCreate) -> Example:
        """Sukurti naują įrašą."""
        db_example = Example(**data.model_dump())
        self.db.add(db_example)
        await self.db.commit()
        await self.db.refresh(db_example)
        return db_example

    async def update(self, example_id: int, data: ExampleUpdate) -> Optional[Example]:
        """Atnaujinti esamą įrašą."""
        db_example = await self.get_by_id(example_id)
        if not db_example:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_example, field, value)

        await self.db.commit()
        await self.db.refresh(db_example)
        return db_example

    async def delete(self, example_id: int) -> bool:
        """Ištrinti įrašą."""
        db_example = await self.get_by_id(example_id)
        if not db_example:
            return False

        await self.db.delete(db_example)
        await self.db.commit()
        return True
```

---

## TypeScript - React Component

```typescript
// frontend/src/components/Example/ExampleCard.tsx

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Edit, Trash2 } from 'lucide-react';

interface Example {
  id: number;
  name: string;
  description?: string;
  value: number;
  isActive: boolean;
  createdAt: string;
}

interface ExampleCardProps {
  example: Example;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

export function ExampleCard({ example, onEdit, onDelete }: ExampleCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(example.id);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">{example.name}</CardTitle>
        <Badge variant={example.isActive ? 'default' : 'secondary'}>
          {example.isActive ? 'Aktyvus' : 'Neaktyvus'}
        </Badge>
      </CardHeader>
      <CardContent>
        {example.description && (
          <p className="text-sm text-muted-foreground mb-4">
            {example.description}
          </p>
        )}

        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-primary">
            {example.value.toFixed(2)}
          </span>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => onEdit(example.id)}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="destructive"
              size="icon"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## TypeScript - API Hook

```typescript
// frontend/src/hooks/useExamples.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

interface Example {
  id: number;
  name: string;
  description?: string;
  value: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface CreateExampleData {
  name: string;
  description?: string;
  value?: number;
  isActive?: boolean;
}

interface UpdateExampleData extends Partial<CreateExampleData> {}

// Gauti visus
export function useExamples() {
  return useQuery({
    queryKey: ['examples'],
    queryFn: async () => {
      const response = await api.get<Example[]>('/examples');
      return response.data;
    },
  });
}

// Gauti vieną
export function useExample(id: number) {
  return useQuery({
    queryKey: ['examples', id],
    queryFn: async () => {
      const response = await api.get<Example>(`/examples/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

// Sukurti
export function useCreateExample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateExampleData) => {
      const response = await api.post<Example>('/examples', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['examples'] });
    },
  });
}

// Atnaujinti
export function useUpdateExample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: UpdateExampleData }) => {
      const response = await api.put<Example>(`/examples/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['examples'] });
      queryClient.invalidateQueries({ queryKey: ['examples', variables.id] });
    },
  });
}

// Ištrinti
export function useDeleteExample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/examples/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['examples'] });
    },
  });
}
```

---

## TypeScript - Zustand Store

```typescript
// frontend/src/stores/exampleStore.ts

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface Example {
  id: number;
  name: string;
  value: number;
}

interface ExampleState {
  // State
  examples: Example[];
  selectedId: number | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setExamples: (examples: Example[]) => void;
  addExample: (example: Example) => void;
  updateExample: (id: number, updates: Partial<Example>) => void;
  removeExample: (id: number) => void;
  selectExample: (id: number | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  examples: [],
  selectedId: null,
  isLoading: false,
  error: null,
};

export const useExampleStore = create<ExampleState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        setExamples: (examples) => set({ examples }, false, 'setExamples'),

        addExample: (example) =>
          set(
            (state) => ({ examples: [...state.examples, example] }),
            false,
            'addExample'
          ),

        updateExample: (id, updates) =>
          set(
            (state) => ({
              examples: state.examples.map((e) =>
                e.id === id ? { ...e, ...updates } : e
              ),
            }),
            false,
            'updateExample'
          ),

        removeExample: (id) =>
          set(
            (state) => ({
              examples: state.examples.filter((e) => e.id !== id),
              selectedId: state.selectedId === id ? null : state.selectedId,
            }),
            false,
            'removeExample'
          ),

        selectExample: (id) => set({ selectedId: id }, false, 'selectExample'),

        setLoading: (isLoading) => set({ isLoading }, false, 'setLoading'),

        setError: (error) => set({ error }, false, 'setError'),

        reset: () => set(initialState, false, 'reset'),
      }),
      {
        name: 'example-storage',
        partialize: (state) => ({ selectedId: state.selectedId }),
      }
    ),
    { name: 'ExampleStore' }
  )
);
```

---

## SQL - Nauja lentelė

```sql
-- Naujos lentelės šablonas

-- Lentelė
CREATE TABLE IF NOT EXISTS example_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    value REAL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    parent_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign keys
    FOREIGN KEY (parent_id) REFERENCES parent_table(id) ON DELETE SET NULL
);

-- Indeksai
CREATE INDEX IF NOT EXISTS idx_example_name ON example_table(name);
CREATE INDEX IF NOT EXISTS idx_example_parent ON example_table(parent_id);
CREATE INDEX IF NOT EXISTS idx_example_active ON example_table(is_active) WHERE is_active = TRUE;

-- Trigeris updated_at atnaujinimui
CREATE TRIGGER IF NOT EXISTS update_example_timestamp
    AFTER UPDATE ON example_table
BEGIN
    UPDATE example_table
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
```

---

*Paskutinis atnaujinimas: 2026-01-10*
