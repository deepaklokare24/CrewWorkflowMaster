'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function WorkflowsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Lease Exit Workflows</h1>
        <Link href="/workflows/new">
          <Button>Create New Workflow</Button>
        </Link>
      </div>

      <div className="grid gap-4">
        {/* Sample workflow card - will be populated dynamically */}
        <Card>
          <CardHeader>
            <CardTitle>Office Space - San Francisco</CardTitle>
            <p className="text-sm text-muted-foreground">Created: Feb 13, 2025</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Status:</span>
                <span className="font-medium text-yellow-500">Under Review</span>
              </div>
              <div className="flex justify-between">
                <span>Lease End Date:</span>
                <span>June 30, 2025</span>
              </div>
              <div className="mt-4">
                <Link href="/workflows/1">
                  <Button variant="outline" size="sm">View Details</Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
