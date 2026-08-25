import { useEffect, useState } from 'react'
import axios from 'axios'

export default function TopCompanies() {
    const [data, setData] = useState([])

    useEffect(() => {
        axios.get(`${import.meta.env.VITE_API_URL}/api/companies/top?limit=15`)
            .then(r => setData(r.data))
    }, [])

    return (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-6">Top Hiring Companies</h2>
            <table className="w-full text-sm">
                <thead>
                    <tr className="text-gray-400 border-b border-gray-800">
                        <th className="text-left py-3">Rank</th>
                        <th className="text-left py-3">Company</th>
                        <th className="text-left py-3">Size</th>
                        <th className="text-right py-3">Job Postings</th>
                        <th className="text-right py-3">Avg Salary</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, i) => (
                        <tr key={i} className="border-b border-gray-800 hover:bg-gray-800 transition-colors">
                            <td className="py-3 text-gray-400">#{row.hiring_rank}</td>
                            <td className="py-3 font-medium">{row.company_name}</td>
                            <td className="py-3 text-gray-400">{row.company_size}</td>
                            <td className="py-3 text-right">{row.job_count?.toLocaleString()}</td>
                            <td className="py-3 text-right text-green-400">
                                ${row.avg_salary?.toLocaleString()}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}