/**
 * SubmissionsListPage - Pateiktų darbų sąrašas
 *
 * Rodo visus patikrintus darbus su filtrais
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Eye,
  FileDown,
  Trash2,
  Filter,
  Search,
  CheckCircle,
  Clock,
  XCircle,
  Loader2,
} from "lucide-react";
import {
  useSubmissions,
  useClasses,
  useTests,
  useGenerateStudentPdf,
  useDeleteSubmission,
} from "@/api/hooks";

export default function SubmissionsListPage() {
  const [selectedClassId, setSelectedClassId] = useState<number | undefined>();
  const [selectedTestId, setSelectedTestId] = useState<number | undefined>();

  const { data: submissions, isLoading } = useSubmissions(
    selectedTestId,
    undefined,
    selectedClassId
  );
  const { data: classes } = useClasses();
  const { data: tests } = useTests();
  const generatePdf = useGenerateStudentPdf();
  const deleteSubmission = useDeleteSubmission();
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  const handleDeleteSubmission = async (id: number) => {
    try {
      await deleteSubmission.mutateAsync(id);
      setDeleteConfirm(null);
    } catch (error) {
      console.error("Trynimo klaida:", error);
      alert("Nepavyko ištrinti darbo");
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <Badge className="bg-green-100 text-green-700">
            <CheckCircle className="w-3 h-3 mr-1" />
            Baigtas
          </Badge>
        );
      case "reviewed":
        return (
          <Badge className="bg-blue-100 text-blue-700">
            <Eye className="w-3 h-3 mr-1" />
            Peržiūrėtas
          </Badge>
        );
      case "processing":
        return (
          <Badge className="bg-amber-100 text-amber-700">
            <Clock className="w-3 h-3 mr-1" />
            Apdorojamas
          </Badge>
        );
      default:
        return <Badge className="bg-gray-100 text-gray-700">{status}</Badge>;
    }
  };

  const getGradeColor = (grade?: number) => {
    if (!grade) return "bg-gray-100 text-gray-600";
    if (grade >= 9) return "bg-green-100 text-green-700";
    if (grade >= 7) return "bg-blue-100 text-blue-700";
    if (grade >= 5) return "bg-amber-100 text-amber-700";
    return "bg-red-100 text-red-700";
  };

  const handleGeneratePdf = async (submissionId: number) => {
    try {
      const result = await generatePdf.mutateAsync({
        submission_id: submissionId,
        include_explanations: true,
      });
      // Atsidarome atsisiuntimo nuorodą
      if (result.download_url) {
        window.open(`/api/v1${result.download_url}`, "_blank");
      }
    } catch (error) {
      console.error("PDF generavimo klaida:", error);
      alert("Nepavyko sugeneruoti PDF");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Patikrinti darbai"
        description="Peržiūrėkite ir eksportuokite mokinių tikrinimo rezultatus"
      />

      {/* Filtrai */}
      <div className="rounded-lg border bg-white p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filtrai:</span>
          </div>

          <select
            value={selectedClassId || ""}
            onChange={(e) =>
              setSelectedClassId(
                e.target.value ? parseInt(e.target.value) : undefined
              )
            }
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="">Visos klasės</option>
            {classes?.map((cls) => (
              <option key={cls.id} value={cls.id}>
                {cls.name}
              </option>
            ))}
          </select>

          <select
            value={selectedTestId || ""}
            onChange={(e) =>
              setSelectedTestId(
                e.target.value ? parseInt(e.target.value) : undefined
              )
            }
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="">Visi kontroliniai</option>
            {tests?.map((test) => (
              <option key={test.id} value={test.id}>
                {test.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Sąrašas */}
      <div className="rounded-lg border bg-white">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            <span className="ml-2 text-gray-600">Kraunama...</span>
          </div>
        ) : submissions && submissions.length > 0 ? (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                  Mokinys
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                  Kontrolinis
                </th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">
                  Taškai
                </th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">
                  Balas
                </th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">
                  Statusas
                </th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">
                  Data
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">
                  Veiksmai
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {submissions.map((sub) => (
                <tr key={sub.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">
                      {sub.student_name}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{sub.test_title}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="font-medium">
                      {sub.total_points}/{sub.max_points}
                    </span>
                    <span className="text-gray-500 text-sm ml-1">
                      ({sub.percentage.toFixed(0)}%)
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {sub.grade && (
                      <span
                        className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${getGradeColor(
                          sub.grade
                        )}`}
                      >
                        {sub.grade}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {getStatusBadge(sub.status)}
                  </td>
                  <td className="px-4 py-3 text-center text-sm text-gray-500">
                    {new Date(sub.submitted_at).toLocaleDateString("lt-LT")}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link to={`/results/${sub.id}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-1" />
                          Peržiūrėti
                        </Button>
                      </Link>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleGeneratePdf(sub.id)}
                        disabled={generatePdf.isPending}
                      >
                        <FileDown className="w-4 h-4 mr-1" />
                        PDF
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setDeleteConfirm(sub.id)}
                        className="text-red-600 hover:bg-red-50 hover:border-red-300"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-gray-500">
            <XCircle className="w-12 h-12 mb-4 text-gray-300" />
            <p className="text-lg font-medium">Nėra patikrintų darbų</p>
            <p className="text-sm mt-1">
              Įkelkite ir patikrinkite mokinių darbus
            </p>
            <Link to="/upload" className="mt-4">
              <Button>Įkelti darbą</Button>
            </Link>
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setDeleteConfirm(null)}
          />
          <div className="relative bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Ištrinti darbą?
            </h3>
            <p className="text-gray-600 mb-6">
              Ar tikrai norite ištrinti šį patikrintą darbą? Šis veiksmas
              negrįžtamas ir bus pašalinti visi tikrinimo rezultatai.
            </p>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setDeleteConfirm(null)}>
                Atšaukti
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleDeleteSubmission(deleteConfirm)}
                disabled={deleteSubmission.isPending}
              >
                {deleteSubmission.isPending ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="w-4 h-4 mr-2" />
                )}
                Ištrinti
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
