'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import WorkflowProgress from '@/components/workflow/WorkflowProgress'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

type WorkflowDetails = {
  id: string
  data: {
    propertyName: string
    propertyType: string
    leaseEndDate: string
    exitReason: string
    createdAt: string
    crew_result?: {
      success: boolean
      result: {
        workflow_creation_status: string
        next_steps: Array<{
          step: string
          details: string
        }>
      }
    }
  }
  state: string
  current_step: string
}

export default function WorkflowDetailPage() {
  const params = useParams()
  const workflowId = params.id as string
  const [workflow, setWorkflow] = useState<WorkflowDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchWorkflow = async () => {
      try {
        setLoading(true)
        const response = await fetch(`/api/workflow/lease-exit/${workflowId}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setWorkflow(data)
        setError('')
      } catch (err) {
        console.error('Failed to fetch workflow:', err)
        setError('Failed to load workflow details. Please try again later.')
      } finally {
        setLoading(false)
      }
    }

    fetchWorkflow()
  }, [workflowId])

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center">
          Loading workflow details...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-destructive/15 text-destructive p-3 rounded-md">
          {error}
        </div>
      </div>
    )
  }

  if (!workflow) {
    return (
      <div className="container mx-auto p-6">
        <div>Workflow not found</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{workflow.data.propertyName}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Property Type:</span>
                <span className="ml-2">{workflow.data.propertyType}</span>
              </div>
              <div>
                <span className="font-medium">Lease End Date:</span>
                <span className="ml-2">
                  {new Date(workflow.data.leaseEndDate).toLocaleDateString()}
                </span>
              </div>
              <div>
                <span className="font-medium">Exit Reason:</span>
                <span className="ml-2">{workflow.data.exitReason}</span>
              </div>
              <div>
                <span className="font-medium">Created:</span>
                <span className="ml-2">
                  {new Date(workflow.data.createdAt).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {workflow.data.crew_result?.success && (
        <Card>
          <CardHeader>
            <CardTitle>Next Steps</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {workflow.data.crew_result.result.next_steps.map((step, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{index + 1}</Badge>
                    <h3 className="font-medium">{step.step}</h3>
                  </div>
                  <p className="text-sm text-muted-foreground pl-8">
                    {step.details}
                  </p>
                  {index < workflow.data.crew_result.result.next_steps.length - 1 && (
                    <Separator className="my-2" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <WorkflowProgress workflowId={workflowId} />
    </div>
  )
} 