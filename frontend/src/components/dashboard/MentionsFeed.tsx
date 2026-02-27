import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Mention } from "@/types";

interface MentionsFeedProps {
  mentions: Mention[];
}

export default function MentionsFeed({ mentions }: MentionsFeedProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Recent Mentions</CardTitle>
      </CardHeader>
      <CardContent>
        {mentions.length === 0 ? (
          <p className="text-sm text-muted-foreground">No mentions detected yet.</p>
        ) : (
          <ul className="space-y-3">
            {mentions.map((mention) => (
              <li key={mention.id} className="border-b pb-2 last:border-0">
                <p className="text-sm">{mention.content}</p>
                <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                  <span>{mention.platform}</span>
                  <span>{mention.sentiment}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
