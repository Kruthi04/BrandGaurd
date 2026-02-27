import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Scout } from "@/types";

interface ScoutListProps {
  scouts: Scout[];
  onDelete?: (scoutId: string) => void;
  onViewUpdates?: (scoutId: string) => void;
}

export default function ScoutList({ scouts, onDelete, onViewUpdates }: ScoutListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Monitoring Scouts</CardTitle>
      </CardHeader>
      <CardContent>
        {scouts.length === 0 ? (
          <p className="text-sm text-muted-foreground">No active scouts. Create one to start monitoring.</p>
        ) : (
          <ul className="space-y-3">
            {scouts.map((scout) => (
              <li key={scout.id} className="flex items-center justify-between border-b pb-2 last:border-0">
                <div>
                  <p className="text-sm font-medium">{scout.display_name}</p>
                  <p className="text-xs text-muted-foreground">{scout.query}</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => onViewUpdates?.(scout.id)}>
                    Updates
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => onDelete?.(scout.id)}>
                    Delete
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
