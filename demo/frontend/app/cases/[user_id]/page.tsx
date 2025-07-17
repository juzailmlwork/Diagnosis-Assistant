"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Search, Plus, User, Calendar, FileText, LogOut } from "lucide-react"
import { API_ENDPOINTS } from "@/lib/config"

interface Case {
  id: number
  user_id: string
  name: string
  age: number
  chief_complaint: string
  previous_medical_history?: string
  imageological_examination?: string
  laboratory_examination?: string
  pathological_examination?: string
  differential_diagnosis: string[]
  final_diagnosis?: string
  reasoning?: string
}

export default function CasesPage({ params }: { params: { user_id: string } }) {
  const [cases, setCases] = useState<Case[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { user_id } = params

  useEffect(() => {
    fetchCases()
  }, [user_id])

  const fetchCases = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.CASES(user_id))
      if (response.ok) {
        const data = await response.json()
        setCases(data.cases || data || [])
      }
    } catch (error) {
      console.error("Error fetching cases:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchCases()
      return
    }

    try {
      const response = await fetch(API_ENDPOINTS.SEARCH, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id,
          query: searchQuery,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setCases(data.cases || data || [])
      }
    } catch (error) {
      console.error("Error searching cases:", error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("user_id")
    router.push("/login")
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-green-500">Loading cases...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-green-500">Doctor AI</h1>
            <p className="text-gray-400">User ID: {user_id}</p>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="border-red-500 text-red-500 hover:bg-red-500 hover:text-white bg-transparent"
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>

        {/* Search and Add New Case */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 flex gap-2">
            <Input
              placeholder="Search by case ID or patient name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-gray-900 border-gray-700 text-white"
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            />
            <Button onClick={handleSearch} className="bg-green-600 hover:bg-green-700">
              <Search className="h-4 w-4" />
            </Button>
          </div>
          <Button onClick={() => router.push(`/cases/${user_id}/add`)} className="bg-green-600 hover:bg-green-700">
            <Plus className="mr-2 h-4 w-4" />
            Add New Case
          </Button>
        </div>

        {/* Cases Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {cases.map((case_item) => (
            <Card
              key={case_item.id}
              className="bg-gray-900 border-gray-700 hover:border-green-500 cursor-pointer transition-colors"
              onClick={() => router.push(`/case/${case_item.id}`)}
            >
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-green-500">Case #{case_item.id}</CardTitle>
                  {case_item.final_diagnosis && <Badge className="bg-green-600">Diagnosed</Badge>}
                </div>
                <CardDescription className="text-gray-400">
                  <div className="flex items-center gap-2 mb-1">
                    <User className="h-4 w-4" />
                    {case_item.name}
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Age: {case_item.age}
                  </div>
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <h4 className="font-semibold text-white mb-1">Chief Complaint:</h4>
                    <p className="text-sm text-gray-300 line-clamp-2">{case_item.chief_complaint}</p>
                  </div>
                  {case_item.differential_diagnosis.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-white mb-1">Differential Diagnosis:</h4>
                      <div className="flex flex-wrap gap-1">
                        {case_item.differential_diagnosis.slice(0, 3).map((diagnosis, index) => (
                          <Badge key={index} variant="outline" className="text-xs border-gray-600 text-gray-300">
                            {diagnosis}
                          </Badge>
                        ))}
                        {case_item.differential_diagnosis.length > 3 && (
                          <Badge variant="outline" className="text-xs border-gray-600 text-gray-300">
                            +{case_item.differential_diagnosis.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                  {case_item.final_diagnosis && (
                    <div>
                      <h4 className="font-semibold text-green-500 mb-1">Final Diagnosis:</h4>
                      <p className="text-sm text-green-400">{case_item.final_diagnosis}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {cases.length === 0 && (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-600 mb-4" />
            <h3 className="text-lg font-semibold text-gray-400 mb-2">No cases found</h3>
            <p className="text-gray-500 mb-4">
              {searchQuery ? "No cases match your search criteria." : "You haven't added any cases yet."}
            </p>
            <Button onClick={() => router.push(`/cases/${user_id}/add`)} className="bg-green-600 hover:bg-green-700">
              <Plus className="mr-2 h-4 w-4" />
              Add Your First Case
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
