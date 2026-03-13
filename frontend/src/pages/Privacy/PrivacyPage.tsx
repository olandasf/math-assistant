import { Shield } from "lucide-react";
import { EmptyState, PageHeader } from "@/components/ui";

export default function PrivacyPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Privatumas"
        description="GDPR ir anonimizacija prieš siunčiant į išorines API (ruošiama)"
      />

      <EmptyState
        icon={<Shield className="h-10 w-10" />}
        title="Privatumo informacija dar ruošiamas"
        description="Čia bus paaiškinta, kaip generuojami unikalūs mokinių kodai ir kaip anonimizuojami duomenys."
      />
    </div>
  );
}
