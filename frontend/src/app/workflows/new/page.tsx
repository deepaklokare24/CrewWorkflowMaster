'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function NewWorkflowPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSubmitting(true)
    setError('')

    const formData = new FormData(event.currentTarget)
    const data = {
      propertyName: formData.get('propertyName'),
      leaseEndDate: formData.get('leaseEndDate'),
      exitReason: formData.get('exitReason'),
      createdAt: new Date().toISOString()
    }

    try {
      const response = await fetch('/api/workflow/lease-exit/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const result = await response.json()
      router.push('/workflows')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create workflow')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Create New Lease Exit Workflow</CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="bg-destructive/15 text-destructive p-3 rounded-md mb-4">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="propertyName" className="text-sm font-medium">
                Property Name
              </label>
              <input
                id="propertyName"
                name="propertyName"
                type="text"
                required
                className="w-full p-2 rounded-md border border-input bg-background"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="leaseEndDate" className="text-sm font-medium">
                Lease End Date
              </label>
              <input
                id="leaseEndDate"
                name="leaseEndDate"
                type="date"
                required
                className="w-full p-2 rounded-md border border-input bg-background"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="exitReason" className="text-sm font-medium">
                Exit Reason
              </label>
              <textarea
                id="exitReason"
                name="exitReason"
                required
                rows={3}
                className="w-full p-2 rounded-md border border-input bg-background"
              />
            </div>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create Workflow'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
