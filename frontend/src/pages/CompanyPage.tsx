import { useEffect, useState } from 'react';
import { companiesApi, Company } from '../api/client';

export default function CompanyPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [showResearch, setShowResearch] = useState(false);
  const [researchParams, setResearchParams] = useState({
    company_name: '',
    website: '',
    job_title: '',
  });
  const [loading, setLoading] = useState(true);
  const [researching, setResearching] = useState(false);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const res = await companiesApi.list();
      setCompanies(res.data);
    } catch (error) {
      console.error('Failed to load companies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setResearching(true);

    try {
      const res = await companiesApi.research(researchParams);

      alert('Research completed!');
      setShowResearch(false);
      setResearchParams({ company_name: '', website: '', job_title: '' });

      await loadCompanies();

      // Select the newly researched company
      if (res.data.company_id) {
        const company = await companiesApi.get(res.data.company_id);
        setSelectedCompany(company.data);
      }
    } catch (error) {
      console.error('Failed to research company:', error);
      alert('Failed to research company');
    } finally {
      setResearching(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Companies</h1>
        <button
          onClick={() => setShowResearch(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Research Company
        </button>
      </div>

      {showResearch && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">Research a Company</h2>
          <form onSubmit={handleResearch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Company Name *</label>
              <input
                type="text"
                required
                value={researchParams.company_name}
                onChange={(e) =>
                  setResearchParams({ ...researchParams, company_name: e.target.value })
                }
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Website (optional)</label>
              <input
                type="url"
                value={researchParams.website}
                onChange={(e) => setResearchParams({ ...researchParams, website: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Job Title Context (optional)
              </label>
              <input
                type="text"
                value={researchParams.job_title}
                onChange={(e) =>
                  setResearchParams({ ...researchParams, job_title: e.target.value })
                }
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                placeholder="e.g., Software Engineering Intern"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={researching}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                {researching ? 'Researching...' : 'Start Research'}
              </button>
              <button
                type="button"
                onClick={() => setShowResearch(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {companies.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">
            No companies researched yet. Start by researching a company!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold">Companies</h2>
              </div>
              <div className="divide-y">
                {companies.map((company) => (
                  <div
                    key={company.id}
                    onClick={() => setSelectedCompany(company)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 ${
                      selectedCompany?.id === company.id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <h3 className="font-medium">{company.name}</h3>
                    <p className="text-sm text-gray-500">{company.industry || 'Unknown industry'}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            {selectedCompany && (
              <div className="space-y-6">
                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h2 className="text-2xl font-bold">{selectedCompany.name}</h2>
                      {selectedCompany.website && (
                        <a
                          href={selectedCompany.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:text-blue-800"
                        >
                          {selectedCompany.website}
                        </a>
                      )}
                    </div>
                    <div className="text-right">
                      {selectedCompany.industry && (
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {selectedCompany.industry}
                        </span>
                      )}
                      {selectedCompany.size && (
                        <p className="text-sm text-gray-500 mt-1">{selectedCompany.size}</p>
                      )}
                    </div>
                  </div>

                  {selectedCompany.description && (
                    <div className="mb-4">
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
                      <p className="text-sm text-gray-600">{selectedCompany.description}</p>
                    </div>
                  )}

                  {selectedCompany.research_summary && (
                    <div className="mb-4">
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Research Summary</h3>
                      <div className="bg-gray-50 p-4 rounded text-sm whitespace-pre-wrap">
                        {selectedCompany.research_summary}
                      </div>
                    </div>
                  )}

                  {selectedCompany.culture_notes && (
                    <div className="mb-4">
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Culture & Values</h3>
                      <div className="bg-gray-50 p-4 rounded text-sm whitespace-pre-wrap">
                        {selectedCompany.culture_notes}
                      </div>
                    </div>
                  )}
                </div>

                {selectedCompany.recent_news && selectedCompany.recent_news.length > 0 && (
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">Recent News</h3>
                    <div className="space-y-4">
                      {selectedCompany.recent_news.map((news: any, idx: number) => (
                        <div key={idx} className="border-l-4 border-blue-500 pl-4">
                          <h4 className="font-medium text-gray-900">{news.title}</h4>
                          {news.url && (
                            <a
                              href={news.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:text-blue-800"
                            >
                              Read more →
                            </a>
                          )}
                          {news.summary && (
                            <p className="text-sm text-gray-600 mt-1">{news.summary}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCompany.key_people && selectedCompany.key_people.length > 0 && (
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">Key People</h3>
                    <div className="space-y-3">
                      {selectedCompany.key_people.map((person: any, idx: number) => (
                        <div key={idx} className="flex items-start">
                          <div className="flex-shrink-0">
                            <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                              <span className="text-sm font-medium text-gray-700">
                                {person.name?.charAt(0) || '?'}
                              </span>
                            </div>
                          </div>
                          <div className="ml-3">
                            <p className="text-sm font-medium text-gray-900">{person.name}</p>
                            <p className="text-sm text-gray-500">{person.title}</p>
                            {person.linkedin_url && (
                              <a
                                href={person.linkedin_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:text-blue-800"
                              >
                                LinkedIn Profile
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
