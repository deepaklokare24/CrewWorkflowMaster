'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function NotificationsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Notifications</h1>

      <div className="grid gap-4">
        {/* Sample notification cards - will be populated dynamically */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Approval Required</CardTitle>
            <p className="text-sm text-muted-foreground">2 minutes ago</p>
          </CardHeader>
          <CardContent>
            <p>New lease exit workflow requires your approval for Office Space - San Francisco</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Form Submission</CardTitle>
            <p className="text-sm text-muted-foreground">1 hour ago</p>
          </CardHeader>
          <CardContent>
            <p>Exit form has been submitted for review</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
