/**
 * Templates Page - Klaidų ir komentarų šablonų valdymas
 */

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { Badge } from "@/components/ui/badge";
import {
  Plus,
  Edit2,
  Trash2,
  Copy,
  Search,
  AlertTriangle,
  MessageSquare,
  Tag,
  Sparkles,
  Save,
  X,
} from "lucide-react";

// Šablono tipai
interface ErrorTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: 'minor' | 'moderate' | 'major';
  pointsDeduction: number;
  explanation: string;
  aiSuggestion?: string;
}

interface CommentTemplate {
  id: string;
  name: string;
  text: string;
  category: string;
  tone: 'positive' | 'neutral' | 'constructive';
}

// Pradiniai klaidų šablonai
const defaultErrorTemplates: ErrorTemplate[] = [
  {
    id: '1',
    name: 'Skaičiavimo klaida',
    description: 'Neteisingas aritmetinis veiksmas',
    category: 'Aritmetika',
    severity: 'moderate',
    pointsDeduction: 0.5,
    explanation: 'Patikrink skaičiavimus dar kartą. Gali būti naudinga apskaičiuoti kiekvieno žingsnio rezultatą atskirai.',
  },
  {
    id: '2',
    name: 'Praleistas veiksmas',
    description: 'Sprendime trūksta tarpinio žingsnio',
    category: 'Metodika',
    severity: 'minor',
    pointsDeduction: 0.25,
    explanation: 'Sprendime turėtų būti matomi visi žingsniai, kad galėtum patikrinti savo darbą.',
  },
  {
    id: '3',
    name: 'Ženklo klaida',
    description: 'Neteisingai pakeistas pliuso/minuso ženklas',
    category: 'Algebra',
    severity: 'moderate',
    pointsDeduction: 0.5,
    explanation: 'Atkreipk dėmesį į ženklų keitimą. Kai pernešame narį į kitą lygties pusę, ženklas keičiasi į priešingą.',
  },
  {
    id: '4',
    name: 'Dalyba iš nulio',
    description: 'Bandyta dalinti iš nulio arba nepatikrinta sąlyga',
    category: 'Algebra',
    severity: 'major',
    pointsDeduction: 1,
    explanation: 'Dalinti iš nulio negalima! Visada patikrink, ar vardiklis nelygus nuliui.',
  },
  {
    id: '5',
    name: 'Neteisingas matavimo vienetas',
    description: 'Naudotas netinkamas arba pamirštas matavimo vienetas',
    category: 'Matavimas',
    severity: 'minor',
    pointsDeduction: 0.25,
    explanation: 'Nepamirški nurodyti matavimo vienetų! Jie yra svarbi atsakymo dalis.',
  },
  {
    id: '6',
    name: 'Formulės klaida',
    description: 'Neteisingai pritaikyta arba užrašyta formulė',
    category: 'Formulės',
    severity: 'major',
    pointsDeduction: 1,
    explanation: 'Patikrink, ar formulė užrašyta teisingai ir ar teisingai įstatėi reikšmes.',
  },
  {
    id: '7',
    name: 'Logikos klaida',
    description: 'Neteisingas samprotavimas arba išvada',
    category: 'Metodika',
    severity: 'major',
    pointsDeduction: 1,
    explanation: 'Perskaityk sąlygą dar kartą ir patikrink, ar tavo samprotavimai logiški.',
  },
  {
    id: '8',
    name: 'Apvalinimo klaida',
    description: 'Neteisingai suapvalintas skaičius',
    category: 'Aritmetika',
    severity: 'minor',
    pointsDeduction: 0.25,
    explanation: 'Prisimink apvalinimo taisykles: jei skaitmuo mažesnis už 5, apvaliname žemyn.',
  },
];

// Pradiniai komentarų šablonai
const defaultCommentTemplates: CommentTemplate[] = [
  {
    id: '1',
    name: 'Puikus darbas',
    text: 'Puikiai atliktas darbas! Visi sprendimai teisingi ir aiškiai užrašyti.',
    category: 'Įvertinimas',
    tone: 'positive',
  },
  {
    id: '2',
    name: 'Geras progresas',
    text: 'Matau, kad stengiesi ir darai pažangą. Taip toliau!',
    category: 'Motyvacija',
    tone: 'positive',
  },
  {
    id: '3',
    name: 'Reikia pasipraktikuoti',
    text: 'Šią temą reikėtų pakartoti. Rekomenduoju atlikti papildomų užduočių.',
    category: 'Patarimas',
    tone: 'constructive',
  },
  {
    id: '4',
    name: 'Neužmirški vienetų',
    text: 'Atsakymuose nepamirški nurodyti matavimo vienetų - tai svarbi sprendimo dalis.',
    category: 'Patarimas',
    tone: 'neutral',
  },
  {
    id: '5',
    name: 'Rašyk aiškiau',
    text: 'Stenkis rašyti aiškiau ir tvarkingiau - tai padės išvengti klaidų ir lengviau tikrinti.',
    category: 'Patarimas',
    tone: 'constructive',
  },
  {
    id: '6',
    name: 'Tikrink atsakymus',
    text: 'Visada patikrink savo atsakymus - įstatyk gautą reikšmę atgal į sąlygą.',
    category: 'Patarimas',
    tone: 'neutral',
  },
];

// Kategorijos
const errorCategories = ['Aritmetika', 'Algebra', 'Metodika', 'Matavimas', 'Formulės', 'Geometrija', 'Kita'];
const commentCategories = ['Įvertinimas', 'Motyvacija', 'Patarimas', 'Kita'];

// Severity badge komponentas
function SeverityBadge({ severity }: { severity: ErrorTemplate['severity'] }) {
  const config = {
    minor: { label: 'Lengva', className: 'bg-yellow-100 text-yellow-800' },
    moderate: { label: 'Vidutinė', className: 'bg-orange-100 text-orange-800' },
    major: { label: 'Rimta', className: 'bg-red-100 text-red-800' },
  };

  const { label, className } = config[severity];
  return <Badge className={className}>{label}</Badge>;
}

// Tone badge komponentas
function ToneBadge({ tone }: { tone: CommentTemplate['tone'] }) {
  const config = {
    positive: { label: 'Teigiamas', className: 'bg-green-100 text-green-800' },
    neutral: { label: 'Neutralus', className: 'bg-gray-100 text-gray-800' },
    constructive: { label: 'Konstruktyvus', className: 'bg-blue-100 text-blue-800' },
  };

  const { label, className } = config[tone];
  return <Badge className={className}>{label}</Badge>;
}

export function TemplatesPage() {
  const [activeTab, setActiveTab] = useState<'errors' | 'comments'>('errors');
  const [errorTemplates, setErrorTemplates] = useState<ErrorTemplate[]>(() => {
    const saved = localStorage.getItem('errorTemplates');
    return saved ? JSON.parse(saved) : defaultErrorTemplates;
  });
  const [commentTemplates, setCommentTemplates] = useState<CommentTemplate[]>(() => {
    const saved = localStorage.getItem('commentTemplates');
    return saved ? JSON.parse(saved) : defaultCommentTemplates;
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [editingError, setEditingError] = useState<ErrorTemplate | null>(null);
  const [editingComment, setEditingComment] = useState<CommentTemplate | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  // Išsaugoti į localStorage
  useEffect(() => {
    localStorage.setItem('errorTemplates', JSON.stringify(errorTemplates));
  }, [errorTemplates]);

  useEffect(() => {
    localStorage.setItem('commentTemplates', JSON.stringify(commentTemplates));
  }, [commentTemplates]);

  // Filtruoti klaidų šablonus
  const filteredErrors = errorTemplates.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Filtruoti komentarų šablonus
  const filteredComments = commentTemplates.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.text.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Ištrinti klaidų šabloną
  const deleteError = (id: string) => {
    setErrorTemplates((prev) => prev.filter((t) => t.id !== id));
  };

  // Ištrinti komentaro šabloną
  const deleteComment = (id: string) => {
    setCommentTemplates((prev) => prev.filter((t) => t.id !== id));
  };

  // Kopijuoti šabloną
  const copyError = (template: ErrorTemplate) => {
    const newTemplate = {
      ...template,
      id: Date.now().toString(),
      name: `${template.name} (kopija)`,
    };
    setErrorTemplates((prev) => [...prev, newTemplate]);
  };

  const copyComment = (template: CommentTemplate) => {
    const newTemplate = {
      ...template,
      id: Date.now().toString(),
      name: `${template.name} (kopija)`,
    };
    setCommentTemplates((prev) => [...prev, newTemplate]);
  };

  // Išsaugoti klaidų šabloną
  const saveError = (template: ErrorTemplate) => {
    if (editingError) {
      setErrorTemplates((prev) =>
        prev.map((t) => (t.id === template.id ? template : t))
      );
    } else {
      setErrorTemplates((prev) => [...prev, { ...template, id: Date.now().toString() }]);
    }
    setEditingError(null);
    setIsCreating(false);
  };

  // Išsaugoti komentaro šabloną
  const saveComment = (template: CommentTemplate) => {
    if (editingComment) {
      setCommentTemplates((prev) =>
        prev.map((t) => (t.id === template.id ? template : t))
      );
    } else {
      setCommentTemplates((prev) => [...prev, { ...template, id: Date.now().toString() }]);
    }
    setEditingComment(null);
    setIsCreating(false);
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      <PageHeader
        title="Šablonai"
        description="Klaidų ir komentarų šablonų valdymas"
      />

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => {
            setActiveTab('errors');
            setSelectedCategory('');
          }}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'errors'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <AlertTriangle className="h-4 w-4 inline mr-2" />
          Klaidų šablonai ({errorTemplates.length})
        </button>
        <button
          onClick={() => {
            setActiveTab('comments');
            setSelectedCategory('');
          }}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'comments'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <MessageSquare className="h-4 w-4 inline mr-2" />
          Komentarų šablonai ({commentTemplates.length})
        </button>
      </div>

      {/* Search and filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Ieškoti šablonų..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <select
          className="h-10 px-3 rounded-md border bg-background min-w-[150px]"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value="">Visos kategorijos</option>
          {(activeTab === 'errors' ? errorCategories : commentCategories).map(
            (cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            )
          )}
        </select>
        <Button
          onClick={() => {
            setIsCreating(true);
            if (activeTab === 'errors') {
              setEditingError({
                id: '',
                name: '',
                description: '',
                category: errorCategories[0],
                severity: 'moderate',
                pointsDeduction: 0.5,
                explanation: '',
              });
            } else {
              setEditingComment({
                id: '',
                name: '',
                text: '',
                category: commentCategories[0],
                tone: 'neutral',
              });
            }
          }}
        >
          <Plus className="h-4 w-4 mr-2" />
          Naujas šablonas
        </Button>
      </div>

      {/* Error Templates */}
      {activeTab === 'errors' && (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredErrors.map((template) => (
            <Card key={template.id} className="relative">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-amber-500" />
                      {template.name}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      {template.description}
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setEditingError(template)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyError(template)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteError(template.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">
                    <Tag className="h-3 w-3 mr-1" />
                    {template.category}
                  </Badge>
                  <SeverityBadge severity={template.severity} />
                  <Badge variant="secondary">-{template.pointsDeduction} tšk.</Badge>
                </div>
                <p className="text-sm text-muted-foreground bg-muted p-2 rounded">
                  <Sparkles className="h-3 w-3 inline mr-1" />
                  {template.explanation}
                </p>
              </CardContent>
            </Card>
          ))}
          {filteredErrors.length === 0 && (
            <div className="col-span-2 text-center py-12 text-muted-foreground">
              Šablonų nerasta
            </div>
          )}
        </div>
      )}

      {/* Comment Templates */}
      {activeTab === 'comments' && (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredComments.map((template) => (
            <Card key={template.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base flex items-center gap-2">
                      <MessageSquare className="h-4 w-4 text-blue-500" />
                      {template.name}
                    </CardTitle>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setEditingComment(template)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyComment(template)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteComment(template.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">
                    <Tag className="h-3 w-3 mr-1" />
                    {template.category}
                  </Badge>
                  <ToneBadge tone={template.tone} />
                </div>
                <p className="text-sm bg-muted p-2 rounded italic">
                  "{template.text}"
                </p>
              </CardContent>
            </Card>
          ))}
          {filteredComments.length === 0 && (
            <div className="col-span-2 text-center py-12 text-muted-foreground">
              Šablonų nerasta
            </div>
          )}
        </div>
      )}

      {/* Edit Error Modal */}
      {editingError && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                {isCreating ? 'Naujas klaidų šablonas' : 'Redaguoti šabloną'}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setEditingError(null);
                    setIsCreating(false);
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Pavadinimas</label>
                <Input
                  value={editingError.name}
                  onChange={(e) =>
                    setEditingError({ ...editingError, name: e.target.value })
                  }
                  placeholder="Klaidos pavadinimas"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Aprašymas</label>
                <Input
                  value={editingError.description}
                  onChange={(e) =>
                    setEditingError({ ...editingError, description: e.target.value })
                  }
                  placeholder="Trumpas aprašymas"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Kategorija</label>
                  <select
                    className="w-full h-10 px-3 rounded-md border bg-background"
                    value={editingError.category}
                    onChange={(e) =>
                      setEditingError({ ...editingError, category: e.target.value })
                    }
                  >
                    {errorCategories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Sunkumas</label>
                  <select
                    className="w-full h-10 px-3 rounded-md border bg-background"
                    value={editingError.severity}
                    onChange={(e) =>
                      setEditingError({
                        ...editingError,
                        severity: e.target.value as ErrorTemplate['severity'],
                      })
                    }
                  >
                    <option value="minor">Lengva</option>
                    <option value="moderate">Vidutinė</option>
                    <option value="major">Rimta</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Taškų atimimas</label>
                <Input
                  type="number"
                  step="0.25"
                  min="0"
                  max="10"
                  value={editingError.pointsDeduction}
                  onChange={(e) =>
                    setEditingError({
                      ...editingError,
                      pointsDeduction: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Paaiškinimas mokiniui</label>
                <textarea
                  className="w-full min-h-[80px] p-3 rounded-md border bg-background"
                  value={editingError.explanation}
                  onChange={(e) =>
                    setEditingError({ ...editingError, explanation: e.target.value })
                  }
                  placeholder="Paaiškinimas, kaip ištaisyti klaidą..."
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setEditingError(null);
                    setIsCreating(false);
                  }}
                >
                  Atšaukti
                </Button>
                <Button onClick={() => saveError(editingError)}>
                  <Save className="h-4 w-4 mr-2" />
                  Išsaugoti
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Edit Comment Modal */}
      {editingComment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                {isCreating ? 'Naujas komentaro šablonas' : 'Redaguoti šabloną'}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setEditingComment(null);
                    setIsCreating(false);
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Pavadinimas</label>
                <Input
                  value={editingComment.name}
                  onChange={(e) =>
                    setEditingComment({ ...editingComment, name: e.target.value })
                  }
                  placeholder="Šablono pavadinimas"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Kategorija</label>
                  <select
                    className="w-full h-10 px-3 rounded-md border bg-background"
                    value={editingComment.category}
                    onChange={(e) =>
                      setEditingComment({ ...editingComment, category: e.target.value })
                    }
                  >
                    {commentCategories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tonas</label>
                  <select
                    className="w-full h-10 px-3 rounded-md border bg-background"
                    value={editingComment.tone}
                    onChange={(e) =>
                      setEditingComment({
                        ...editingComment,
                        tone: e.target.value as CommentTemplate['tone'],
                      })
                    }
                  >
                    <option value="positive">Teigiamas</option>
                    <option value="neutral">Neutralus</option>
                    <option value="constructive">Konstruktyvus</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Komentaro tekstas</label>
                <textarea
                  className="w-full min-h-[100px] p-3 rounded-md border bg-background"
                  value={editingComment.text}
                  onChange={(e) =>
                    setEditingComment({ ...editingComment, text: e.target.value })
                  }
                  placeholder="Komentaro tekstas mokiniui..."
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setEditingComment(null);
                    setIsCreating(false);
                  }}
                >
                  Atšaukti
                </Button>
                <Button onClick={() => saveComment(editingComment)}>
                  <Save className="h-4 w-4 mr-2" />
                  Išsaugoti
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
