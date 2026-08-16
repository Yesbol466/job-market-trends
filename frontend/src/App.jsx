import { useState } from 'react'
import SkillDemand from './pages/SkillDemand'
import SalaryByRole from './pages/SalaryByRole'
import HiringByCountry from './pages/HiringByCountry'
import TopCompanies from './pages/TopCompanies'
import Summary from './components/Summary'

const tabs = [
  { id: 'skills', label: 'Skill Demand' },
  { id: 'salary', label: 'Salary by Role' },
  { id: 'location', label: 'Hiring by Country' },
  { id: 'companies', label: 'Top Companies' },
]

export default function App() {
  const [active, setActive] = useState('skills')

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">
            Job Market Trends
          </h1>
          <p className="text-gray-400 mt-1">
            Analytics dashboard powered by 1.6M job postings
          </p>
        </div>

        {/* Summary Cards */}
        <Summary />

        {/* Tabs */}
        <div className="flex gap-2 mt-8 mb-6 border-b border-gray-800">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${active === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Pages */}
        {active === 'skills' && <SkillDemand />}
        {active === 'salary' && <SalaryByRole />}
        {active === 'location' && <HiringByCountry />}
        {active === 'companies' && <TopCompanies />}

      </div>
    </div>
  )
}