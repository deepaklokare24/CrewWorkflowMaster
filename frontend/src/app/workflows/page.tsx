'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

type Workflow = {
  id: string
  data: {
    propertyName: string
    leaseEndDate: string
    exitReason: string
    createdAt: string
  }
  state: string
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchWorkflows() {
      try {
        const response = await fetch('/api/workflow/lease-exit/list')
        if (!response.ok) {
          throw new Error('Failed to fetch workflows')
        }
        const data = await response.json()
        setWorkflows(data)
      } catch (err) {
        setError('Failed to load workflows')
      } finally {
        setLoading(false)
      }
    }

    fetchWorkflows()
  }, [])

  function getStateColor(state: string) {
    const colors = {
      draft: 'text-yellow-500',
      'under-review': 'text-blue-500',
      approved: 'text-green-500',
      rejected: 'text-red-500'
    }
    return colors[state as keyof typeof colors] || 'text-gray-500'
  }

  if (loading) {
    return <div>Loading workflows...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Lease Exit Workflows</h1>
        <Link href="/workflows/new">
          <Button>Create New Workflow</Button>
        </Link>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive p-3 rounded-md">
          {error}
        </div>
      )}

      <div className="grid gap-4">
        {workflows.length > 0 ? (
          workflows.map((workflow) => (
            <Card key={workflow.id}>
              <CardHeader>
                <CardTitle>{workflow.data.propertyName}</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Created: {new Date(workflow.data.createdAt).toLocaleDateString()}
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className={getStateColor(workflow.state)}>
                      {workflow.state}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Lease End Date:</span>
                    <span>
                      {new Date(workflow.data.leaseEndDate).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="mt-4">
                    <Link href={`/workflows/${workflow.id}`}>
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              No workflows found. Create your first workflow to get started.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}