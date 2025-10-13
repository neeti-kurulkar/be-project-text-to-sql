import { Link } from 'react-router-dom';
import { Database, FileText, MessageSquare, BarChart3, Brain, Sparkles } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-lg">
                <Database className="h-16 w-16 text-white" />
              </div>
            </div>

            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6">
              HUL Financial Analysis
            </h1>

            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              AI-powered financial data analysis with intelligent visualization.
              Ask questions in natural language and get instant insights from HUL's financial data.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/ask"
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl flex items-center space-x-2 text-lg font-semibold"
              >
                <MessageSquare className="h-5 w-5" />
                <span>Ask a Question</span>
              </Link>

              <Link
                to="/summary"
                className="px-8 py-4 bg-white text-gray-900 rounded-lg hover:bg-gray-50 transition-all shadow-md hover:shadow-lg flex items-center space-x-2 text-lg font-semibold border border-gray-200"
              >
                <FileText className="h-5 w-5" />
                <span>View Summary</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Powerful Features
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border border-gray-100">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <MessageSquare className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 text-center">
                Natural Language Queries
              </h3>
              <p className="text-gray-600 text-center">
                Ask questions in plain English. Our AI converts them into SQL queries and retrieves the data you need.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border border-gray-100">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-indigo-100 rounded-lg">
                  <BarChart3 className="h-8 w-8 text-indigo-600" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 text-center">
                Smart Visualizations
              </h3>
              <p className="text-gray-600 text-center">
                Automatic chart generation based on your data. See trends, patterns, and insights at a glance.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border border-gray-100">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Brain className="h-8 w-8 text-purple-600" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 text-center">
                AI-Powered Insights
              </h3>
              <p className="text-gray-600 text-center">
                Get intelligent analysis and summaries. Understand complex financial data with AI-generated insights.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Actions Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white bg-opacity-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Get Started
          </h2>

          <div className="grid sm:grid-cols-3 gap-6">
            <Link
              to="/summary"
              className="group p-6 bg-white rounded-xl shadow-md hover:shadow-xl transition-all border-2 border-transparent hover:border-blue-500"
            >
              <div className="flex justify-center mb-4">
                <FileText className="h-12 w-12 text-blue-600 group-hover:scale-110 transition-transform" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2 text-center">
                Financial Summary
              </h3>
              <p className="text-sm text-gray-600 text-center">
                View comprehensive analysis of HUL's financial data (2021-2025)
              </p>
            </Link>

            <Link
              to="/ask"
              className="group p-6 bg-white rounded-xl shadow-md hover:shadow-xl transition-all border-2 border-transparent hover:border-indigo-500"
            >
              <div className="flex justify-center mb-4">
                <MessageSquare className="h-12 w-12 text-indigo-600 group-hover:scale-110 transition-transform" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2 text-center">
                Ask Questions
              </h3>
              <p className="text-sm text-gray-600 text-center">
                Query financial data using natural language and get instant results
              </p>
            </Link>

            <Link
              to="/documents"
              className="group p-6 bg-white rounded-xl shadow-md hover:shadow-xl transition-all border-2 border-transparent hover:border-purple-500"
            >
              <div className="flex justify-center mb-4">
                <Database className="h-12 w-12 text-purple-600 group-hover:scale-110 transition-transform" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2 text-center">
                Source Documents
              </h3>
              <p className="text-sm text-gray-600 text-center">
                Access original financial statements from Moneycontrol
              </p>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-2xl p-12">
            <div className="grid md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="flex justify-center mb-2">
                  <Sparkles className="h-8 w-8 text-blue-200" />
                </div>
                <div className="text-4xl font-bold text-white mb-2">4</div>
                <div className="text-blue-100">AI Agents</div>
              </div>

              <div>
                <div className="flex justify-center mb-2">
                  <Database className="h-8 w-8 text-blue-200" />
                </div>
                <div className="text-4xl font-bold text-white mb-2">5 Years</div>
                <div className="text-blue-100">Financial Data</div>
              </div>

              <div>
                <div className="flex justify-center mb-2">
                  <BarChart3 className="h-8 w-8 text-blue-200" />
                </div>
                <div className="text-4xl font-bold text-white mb-2">Auto</div>
                <div className="text-blue-100">Visualizations</div>
              </div>

              <div>
                <div className="flex justify-center mb-2">
                  <Brain className="h-8 w-8 text-blue-200" />
                </div>
                <div className="text-4xl font-bold text-white mb-2">Smart</div>
                <div className="text-blue-100">AI Insights</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 sm:px-6 lg:px-8 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>© 2025 HUL Financial Analysis System</p>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span>System Active</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
