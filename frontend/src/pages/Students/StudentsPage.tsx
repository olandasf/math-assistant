/**
 * Mokiniai puslapis - mokinių sąrašas ir valdymas
 */

import { useState, useMemo } from "react";
import {
  User,
  Plus,
  Edit,
  Trash2,
  Search,
  Upload,
  ChevronDown,
  UserCheck,
  UserX,
} from "lucide-react";
import {
  useStudents,
  useClasses,
  useActiveSchoolYear,
  useCreateStudent,
  useUpdateStudent,
  useDeleteStudent,
  useBulkCreateStudents,
} from "@/api/hooks";
import type { Student, StudentCreate, StudentUpdate } from "@/api/types";
import {
  PageHeader,
  PageLoader,
  EmptyState,
  Modal,
  Button,
  Input,
  Select,
  Textarea,
  Card,
  Badge,
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui";

export default function StudentsPage() {
  const { data: activeYear } = useActiveSchoolYear();
  const { data: classes } = useClasses(activeYear?.id);

  // Filters
  const [selectedClassId, setSelectedClassId] = useState<number | undefined>();
  const [searchQuery, setSearchQuery] = useState("");
  const [showInactive, setShowInactive] = useState(false);

  const { data: students, isLoading, error } = useStudents(selectedClassId);

  const createMutation = useCreateStudent();
  const updateMutation = useUpdateStudent();
  const deleteMutation = useDeleteStudent();
  const bulkCreateMutation = useBulkCreateStudents();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isBulkModalOpen, setIsBulkModalOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Student | null>(null);

  // Form state
  const [formData, setFormData] = useState<StudentCreate>({
    first_name: "",
    last_name: "",
    class_id: 0,
    notes: "",
  });

  // Bulk import state
  const [bulkText, setBulkText] = useState("");
  const [bulkClassId, setBulkClassId] = useState<number>(0);

  // Filter students
  const filteredStudents = useMemo(() => {
    if (!students) return [];

    return students.filter((student) => {
      // Filter by active status
      if (!showInactive && !student.is_active) return false;

      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const fullName =
          `${student.first_name} ${student.last_name}`.toLowerCase();
        const code = student.unique_code.toLowerCase();
        if (!fullName.includes(query) && !code.includes(query)) return false;
      }

      return true;
    });
  }, [students, searchQuery, showInactive]);

  // Group by class
  const studentsByClass = useMemo(() => {
    const groups: Record<number, Student[]> = {};
    filteredStudents.forEach((student) => {
      if (!groups[student.class_id]) {
        groups[student.class_id] = [];
      }
      groups[student.class_id].push(student);
    });
    return groups;
  }, [filteredStudents]);

  const getClassName = (classId: number) => {
    return classes?.find((c) => c.id === classId)?.name || "Nežinoma";
  };

  const openCreateModal = () => {
    setEditingStudent(null);
    setFormData({
      first_name: "",
      last_name: "",
      class_id: selectedClassId || classes?.[0]?.id || 0,
      notes: "",
    });
    setIsModalOpen(true);
  };

  const openEditModal = (student: Student) => {
    setEditingStudent(student);
    setFormData({
      first_name: student.first_name,
      last_name: student.last_name,
      class_id: student.class_id,
      notes: student.notes || "",
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (editingStudent) {
      const update: StudentUpdate = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        class_id: formData.class_id,
        notes: formData.notes,
      };
      await updateMutation.mutateAsync({
        id: editingStudent.id,
        payload: update,
      });
    } else {
      await createMutation.mutateAsync(formData);
    }

    setIsModalOpen(false);
  };

  const handleDelete = async () => {
    if (deleteConfirm) {
      await deleteMutation.mutateAsync(deleteConfirm.id);
      setDeleteConfirm(null);
    }
  };

  const handleBulkImport = async () => {
    if (!bulkText.trim() || !bulkClassId) return;

    // Parse names - one per line, format: "Vardas Pavardė"
    const lines = bulkText
      .trim()
      .split("\n")
      .filter((line) => line.trim());
    const students: StudentCreate[] = lines.map((line) => {
      const parts = line.trim().split(/\s+/);
      const firstName = parts[0] || "";
      const lastName = parts.slice(1).join(" ") || "";
      return {
        first_name: firstName,
        last_name: lastName,
        class_id: bulkClassId,
      };
    });

    if (students.length > 0) {
      await bulkCreateMutation.mutateAsync({ students });
      setIsBulkModalOpen(false);
      setBulkText("");
    }
  };

  if (isLoading) {
    return <PageLoader text="Kraunami mokiniai..." />;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <div className="p-4 text-red-600">
          Klaida kraunant mokinius: {error.message}
        </div>
      </Card>
    );
  }

  return (
    <div>
      <PageHeader
        title="Mokiniai"
        description={`Iš viso: ${filteredStudents.length} mokinių`}
        actions={
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => {
                setBulkClassId(selectedClassId || classes?.[0]?.id || 0);
                setIsBulkModalOpen(true);
              }}
            >
              <Upload className="h-4 w-4 mr-2" />
              Importuoti
            </Button>
            <Button onClick={openCreateModal}>
              <Plus className="h-4 w-4 mr-2" />
              Naujas mokinys
            </Button>
          </div>
        }
      />

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4">
        {/* Search */}
        <div className="relative flex-1 min-w-64">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Ieškoti pagal vardą arba kodą..."
            className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm transition-all focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
          />
        </div>

        {/* Class filter */}
        <div className="relative">
          <select
            value={selectedClassId || ""}
            onChange={(e) =>
              setSelectedClassId(
                e.target.value ? parseInt(e.target.value) : undefined
              )
            }
            className="appearance-none rounded-xl border border-slate-200 bg-white py-2.5 pl-4 pr-10 text-sm transition-all focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
          >
            <option value="">Visos klasės</option>
            {classes?.map((cls) => (
              <option key={cls.id} value={cls.id}>
                {cls.name}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        </div>

        {/* Show inactive toggle */}
        <Button
          variant={showInactive ? "default" : "outline"}
          onClick={() => setShowInactive(!showInactive)}
        >
          {showInactive ? (
            <UserCheck className="h-4 w-4 mr-2" />
          ) : (
            <UserX className="h-4 w-4 mr-2" />
          )}
          {showInactive ? "Rodyti aktyvius" : "Rodyti neaktyvius"}
        </Button>
      </div>

      {/* Students list */}
      {!filteredStudents.length ? (
        <EmptyState
          icon={<User className="h-12 w-12" />}
          title={searchQuery ? "Nieko nerasta" : "Nėra mokinių"}
          description={
            searchQuery
              ? "Pabandykite kitą paieškos užklausą"
              : "Pridėkite mokinius į klases"
          }
          action={
            searchQuery
              ? undefined
              : {
                  label: "Pridėti mokinį",
                  onClick: openCreateModal,
                }
          }
        />
      ) : selectedClassId ? (
        // Single class view
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Kodas</TableHead>
              <TableHead>Vardas</TableHead>
              <TableHead>Pavardė</TableHead>
              <TableHead>Pastabos</TableHead>
              <TableHead className="text-right">Veiksmai</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredStudents.map((student) => (
              <StudentRow
                key={student.id}
                student={student}
                onEdit={() => openEditModal(student)}
                onDelete={() => setDeleteConfirm(student)}
              />
            ))}
          </TableBody>
        </Table>
      ) : (
        // Grouped by class view
        <div className="space-y-6">
          {Object.entries(studentsByClass).map(([classId, classStudents]) => (
            <Card key={classId} className="overflow-hidden">
              <div className="border-b border-slate-100 bg-slate-50 px-4 py-3">
                <h3 className="font-semibold text-slate-800">
                  {getClassName(parseInt(classId))}
                  <Badge variant="info" className="ml-2">
                    {classStudents.length} mokinių
                  </Badge>
                </h3>
              </div>
              <table className="w-full">
                <thead className="border-b bg-gray-50/50">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                      Kodas
                    </th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                      Vardas
                    </th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                      Pavardė
                    </th>
                    <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">
                      Veiksmai
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {classStudents.map((student) => (
                    <StudentRow
                      key={student.id}
                      student={student}
                      onEdit={() => openEditModal(student)}
                      onDelete={() => setDeleteConfirm(student)}
                      compact
                    />
                  ))}
                </tbody>
              </table>
            </Card>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingStudent ? "Redaguoti mokinį" : "Naujas mokinys"}
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Atšaukti
            </Button>
            <Button
              onClick={handleSubmit}
              isLoading={createMutation.isPending || updateMutation.isPending}
            >
              {editingStudent ? "Išsaugoti" : "Sukurti"}
            </Button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Vardas
              </label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) =>
                  setFormData({ ...formData, first_name: e.target.value })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Pavardė
              </label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) =>
                  setFormData({ ...formData, last_name: e.target.value })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Klasė
            </label>
            <select
              value={formData.class_id}
              onChange={(e) =>
                setFormData({ ...formData, class_id: parseInt(e.target.value) })
              }
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            >
              <option value={0} disabled>
                Pasirinkite klasę
              </option>
              {classes?.map((cls) => (
                <option key={cls.id} value={cls.id}>
                  {cls.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Pastabos
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
              rows={2}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </form>
      </Modal>

      {/* Bulk Import Modal */}
      <Modal
        isOpen={isBulkModalOpen}
        onClose={() => setIsBulkModalOpen(false)}
        title="Importuoti mokinius"
        size="lg"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setIsBulkModalOpen(false)}
            >
              Atšaukti
            </Button>
            <Button
              onClick={handleBulkImport}
              isLoading={bulkCreateMutation.isPending}
            >
              Importuoti
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Klasė
            </label>
            <select
              value={bulkClassId}
              onChange={(e) => setBulkClassId(parseInt(e.target.value))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              required
            >
              <option value={0} disabled>
                Pasirinkite klasę
              </option>
              {classes?.map((cls) => (
                <option key={cls.id} value={cls.id}>
                  {cls.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Mokinių sąrašas (vienas per eilutę: Vardas Pavardė)
            </label>
            <textarea
              value={bulkText}
              onChange={(e) => setBulkText(e.target.value)}
              rows={10}
              placeholder="Jonas Jonaitis&#10;Petras Petraitis&#10;Ona Onaitė"
              className="w-full font-mono rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <p className="text-sm text-gray-500">
            Įvedėte{" "}
            {
              bulkText
                .trim()
                .split("\n")
                .filter((l) => l.trim()).length
            }{" "}
            mokinių
          </p>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Ištrinti mokinį?"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>
              Atšaukti
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              isLoading={deleteMutation.isPending}
            >
              Ištrinti
            </Button>
          </>
        }
      >
        <p className="text-gray-600">
          Ar tikrai norite ištrinti mokinį{" "}
          <strong>
            {deleteConfirm?.first_name} {deleteConfirm?.last_name}
          </strong>
          ? Šis veiksmas negrįžtamas.
        </p>
      </Modal>
    </div>
  );
}

// Student row component
interface StudentRowProps {
  student: Student;
  onEdit: () => void;
  onDelete: () => void;
  compact?: boolean;
}

function StudentRow({ student, onEdit, onDelete, compact }: StudentRowProps) {
  return (
    <tr
      className={`transition-colors hover:bg-slate-50 ${
        !student.is_active ? "bg-slate-50/50 text-slate-400" : ""
      }`}
    >
      <td className="px-4 py-3 text-sm font-mono text-sky-600">
        {student.unique_code}
      </td>
      <td className="px-4 py-3 text-sm text-slate-700">{student.first_name}</td>
      <td className="px-4 py-3 text-sm font-medium text-slate-900">
        {student.last_name}
      </td>
      {!compact && (
        <td className="px-4 py-3 text-sm text-slate-500">
          {student.notes || "-"}
        </td>
      )}
      <td className="px-4 py-3 text-right">
        <div className="flex justify-end gap-1">
          <button
            onClick={onEdit}
            className="rounded-lg p-2 text-slate-400 transition-all hover:bg-sky-50 hover:text-sky-600"
            title="Redaguoti"
          >
            <Edit className="h-4 w-4" />
          </button>
          <button
            onClick={onDelete}
            className="rounded-lg p-2 text-slate-400 transition-all hover:bg-red-50 hover:text-red-600"
            title="Ištrinti"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </td>
    </tr>
  );
}
