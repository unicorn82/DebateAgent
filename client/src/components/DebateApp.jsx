import { useState, useEffect } from 'react';
import { 
  FaRobot, 
  FaGavel, 
  FaTrophy, 
  FaDownload,
  FaSpinner,
  FaExpandAlt,
  FaTimes,
  FaEye,
  FaEyeSlash
} from 'react-icons/fa';
import * as api from '../services/api';
import { TeamContext, JudgeContext } from '../models/DebateContext';
import './DebateApp.css';

const DebateApp = () => {
  const [topic, setTopic] = useState('');
  const [affContext, setAffContext] = useState(new TeamContext('affirmative', 1));
  const [negContext, setNegContext] = useState(new TeamContext('negative', 2));
  const [judgeContext, setJudgeContext] = useState(new JudgeContext(3));
  
  const [loading, setLoading] = useState({});
  const [statusMessage, setStatusMessage] = useState('');
  const [providers, setProviders] = useState([]);
  const [modalData, setModalData] = useState(null); // { title, content, onSave }
  const [token, setToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [requestCount, setRequestCount] = useState(null);

  // Sync token with API service
  useEffect(() => {
    api.setAuthToken(token);
  }, [token]);

  // Load token from cookie on mount
  useEffect(() => {
    const getCookie = (name) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    };
    
    const savedToken = getCookie('debate_token');
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  // Fetch token info when token is set
  useEffect(() => {
    if (token) {
      const fetchInfo = async () => {
        try {
          const result = await api.getTokenInfo();
          if (result.request_count !== undefined) {
            setRequestCount(result.request_count);
          }
        } catch (error) {
          console.error("Failed to fetch token info:", error);
          setRequestCount(null);
        }
      };
      fetchInfo();
    } else {
      setRequestCount(null);
    }
  }, [token]);

  const handleTokenSubmit = async () => {
    if (!token.trim()) {
      setStatusMessage('⚠️ Please enter an access token.');
      return;
    }

    setLoading({ ...loading, token: true });
    try {
      const result = await api.getTokenInfo();
      setRequestCount(result.request_count);
      
      // Save to cookie only after successful validation (expires in 7 days)
      const d = new Date();
      d.setTime(d.getTime() + (7 * 24 * 60 * 60 * 1000));
      document.cookie = `debate_token=${token};expires=${d.toUTCString()};path=/`;
      
      setStatusMessage('✅ Token saved and validated!');
    } catch (error) {
      setStatusMessage(`❌ Invalid token: ${error.response?.data?.detail || error.message}`);
      setRequestCount(null);
    } finally {
      setLoading({ ...loading, token: false });
    }
  };

  // Fetch providers on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await api.getProviders();
        setProviders(result.providers || []);
      } catch (error) {
        console.error("Failed to fetch configuration:", error);
      }
    };
    fetchData();
  }, []);

  const handleProviderChange = (role, providerId) => {
    const id = parseInt(providerId);
    if (role === 'affirmative') {
      setAffContext(prev => ({ ...prev, providerId: id }));
    } else if (role === 'negative') {
      setNegContext(prev => ({ ...prev, providerId: id }));
    } else if (role === 'referee') {
      setJudgeContext(prev => ({ ...prev, providerId: id }));
    }

  };

  // Handle generate topics
  const handleGenerateTopics = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, topics: true });
    setStatusMessage('');
    
    try {
      const result = await api.generateTopics(topic);
      setAffContext(prev => ({ ...prev, options: result.affirmative_option }));
      setNegContext(prev => ({ ...prev, options: result.negative_option }));
      setStatusMessage('✅ Topics generated successfully!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, topics: false });
    }
  };

  // Handle generate affirmative option only
  const handleGenerateAffOption = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, affOption: true });
    try {
      console.log("topic", topic);
      const result = await api.generateAffirmativeOption(topic, affContext.providerId);
      console.log("result", result);
      setAffContext(prev => ({ ...prev, options: result.statement }));
      if (result.request_count !== undefined) setRequestCount(result.request_count);
      setStatusMessage('✅ Affirmative option generated!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, affOption: false });
    }
  };

  // Handle generate negative option only
  const handleGenerateNegOption = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, negOption: true });
    try {
      const result = await api.generateNegativeOption(topic, negContext.providerId);
      setNegContext(prev => ({ ...prev, options: result.statement }));
      if (result.request_count !== undefined) setRequestCount(result.request_count);
      setStatusMessage('✅ Negative option generated!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, negOption: false });
    }
  };

  // Collect all statements for a team
  const collectStatements = (role) => {
    const context = role === 'aff' ? affContext : negContext;
    return context.statements.filter(s => s && s.trim());
  };

  // Handle generate statement for a specific round
  const handleGenerateStatement = async (roundKey, team) => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    const loadingKey = `${roundKey}_${team}`;
    setLoading({ ...loading, [loadingKey]: true });
    
    try {
      const affStatements = collectStatements('aff');
      const negStatements = collectStatements('neg');
      
      const data = {
        topic,
        aff_options: affContext.options,
        neg_options: negContext.options,
        affirmative_statements: affStatements,
        negative_statements: negStatements,
        context: `Round ${roundKey.replace('round', '')} argument`,
        provider_id: team === 'aff' ? affContext.providerId : negContext.providerId
      };
      
      let result;
      if (team === 'aff') {
        result = await api.generateAffirmativeStatement(data);
        setAffContext(prev => {
          const newStmts = [...prev.statements];
          const idx = parseInt(roundKey.replace('round', '')) - 1;
          newStmts[idx] = result.statement;
          return { ...prev, statements: newStmts };
        });
      } else {
        result = await api.generateNegativeStatement(data);
        setNegContext(prev => {
          const newStmts = [...prev.statements];
          const idx = parseInt(roundKey.replace('round', '')) - 1;
          newStmts[idx] = result.statement;
          return { ...prev, statements: newStmts };
        });
      }
      
      if (result.request_count !== undefined) setRequestCount(result.request_count);
      setStatusMessage(`✅ ${team === 'aff' ? 'Affirmative' : 'Negative'} statement generated!`);
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, [loadingKey]: false });
    }
  };

  // Handle generate closing argument
  const handleGenerateClosing = async (team) => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    const loadingKey = `closing_${team}`;
    setLoading({ ...loading, [loadingKey]: true });
    
    try {
      const affStatements = collectStatements('aff');
      const negStatements = collectStatements('neg');
      
      const data = {
        topic,
        aff_options: affContext.options,
        neg_options: negContext.options,
        team_statements: team === 'aff' ? affStatements : negStatements,
        opponent_statements: team === 'aff' ? negStatements : affStatements,
        provider_id: team === 'aff' ? affContext.providerId : negContext.providerId
      };
      
      let result;
      if (team === 'aff') {
        result = await api.generateAffirmativeClosing(data);
        setAffContext(prev => ({ ...prev, finalSummary: result.statement }));
      } else {
        result = await api.generateNegativeClosing(data);
        setNegContext(prev => ({ ...prev, finalSummary: result.statement }));
      }
      
      if (result.request_count !== undefined) setRequestCount(result.request_count);
      setStatusMessage(`✅ ${team === 'aff' ? 'Affirmative' : 'Negative'} closing generated!`);
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, [loadingKey]: false });
    }
  };

  // Handle judge debate
  const handleJudge = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, judge: true });
    setStatusMessage('⚖️ Judging debate...');
    
    try {
      const affStatements = collectStatements('aff');
      const negStatements = collectStatements('neg');
      
      const data = {
        topic,
        aff_options: affContext.options,
        neg_options: negContext.options,
        affirmative_statements: affStatements,
        negative_statements: negStatements,
        aff_final: affContext.finalSummary,
        neg_final: negContext.finalSummary,
        provider_id: judgeContext.providerId
      };
      
      const result = await api.judgeDebate(data);
      
      // Parse the result if it's a JSON string
      let parsedResult;
      try {
        let cleanResult = result.result;
        if (typeof cleanResult === 'string') {
          // Remove markdown code blocks if present
          cleanResult = cleanResult.replace(/```json/g, '').replace(/```/g, '').trim();
          parsedResult = JSON.parse(cleanResult);
        } else {
          parsedResult = result.result;
        }
      } catch (e) {
        console.error("Failed to parse judge result:", e);
        parsedResult = { result: result.result };
      }
      
      setJudgeContext(prev => ({ ...prev, result: parsedResult }));
      if (result.request_count !== undefined) setRequestCount(result.request_count);
      setStatusMessage('✅ Judging complete!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, judge: false });
    }
  };

  // Download transcript
  const handleDownloadTranscript = () => {
    const affStatements = collectStatements('aff');
    const negStatements = collectStatements('neg');
    
    // Generate rounds content
    let roundsContent = '';
    const maxRounds = Math.max(affStatements.length, negStatements.length);
    
    for (let i = 0; i < maxRounds; i++) {
        roundsContent += `# Round ${i + 1}\n\n`;
        
        if (affStatements[i]) {
            roundsContent += `# Affirmative Argument\n\n${affStatements[i]}\n\n`;
        }
        
        if (negStatements[i]) {
            roundsContent += `# Negative Argument\n\n${negStatements[i]}\n\n`;
        }
    }

    const transcript = `***This is a AI debate multi-agents which simulates a formal, competitive debate between two opposing sides on a given resolution. And judge agent evaluates both sides using impact weighing (magnitude, probability, timeframe) and issues a final judgment.***

# 🏆 Leaderboard

|Model|Score|
|:-|:-|
|OpenAI-ChatGPT|1|
|Google-Gemini|0|
|Deepseek|1|

# DEBATE TRANSCRIPT

## Affirmative Team Agent: ${providers.find(p => p.id === affContext.providerId)?.model || 'gemini-3-flash-preview'}

## Negative Team Agent: ${providers.find(p => p.id === negContext.providerId)?.model || 'deepseek-chat'}

## Judge Agent: ${providers.find(p => p.id === judgeContext.providerId)?.model || 'gpt-5-mini'}

**Topic:** ${topic}

# Affirmative Team Options

${affContext.options}

# Negative Team Options

${negContext.options}

${roundsContent}# Affirmative Final Summary

${affContext.finalSummary}

# Negative Final Summary

${negContext.finalSummary}

${judgeContext.result ? `## 🎉 Congratulations to the Winner! 🎉

### 🏆 Judge’s Decision

**Winner:** **${judgeContext.result.winner?.toUpperCase() || 'N/A'}**  
**Affirmative Score:** ${judgeContext.result.winner?.toLowerCase() === 'affirmative' ? `**${judgeContext.result.affirmative_score || 'N/A'}**` : (judgeContext.result.affirmative_score || 'N/A')}  
**Negative Score:** ${judgeContext.result.winner?.toLowerCase() === 'negative' ? `**${judgeContext.result.negative_score || 'N/A'}**` : (judgeContext.result.negative_score || 'N/A')}

---

### 🧠 Reason for Decision

${judgeContext.result.reason || 'N/A'}

👏 **Congratulations to the ${judgeContext.result.winner || 'winning'} team on a strong, evidence-driven victory!**` : ''}
`;

    const blob = new Blob([transcript], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const fileName = topic ? topic.slice(0, 50).replace(/[^a-z0-9]/gi, '_') : 'debate_transcript';
    a.download = `${fileName}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="debate-app">
      <header className="app-header">
        <h1>🗣️ Debate App</h1>
        <p>Enter a topic, auto-generate team options, run multiple rounds, write final summaries, then have an AI judge pick a winner.</p>
        
        <div className="header-controls">
          <div className="token-input-section">
            <div className="token-input-group">
              <div className="password-wrapper">
                <input
                  type={showToken ? "text" : "password"}
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="Enter Access Token"
                  className="header-token-input"
                />
                <button 
                  type="button"
                  className="token-toggle-btn"
                  onClick={() => setShowToken(!showToken)}
                  title={showToken ? "Hide Token" : "Show Token"}
                >
                  {showToken ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
              <button 
                className="btn btn-primary btn-sm"
                onClick={handleTokenSubmit}
                disabled={loading.token}
              >
                {loading.token ? <FaSpinner className="spin" /> : 'Validate Token'}
              </button>
            </div>
          </div>

          {requestCount !== null && (
            <div className="request-count-badge">
              Remaining Requests: <strong>{requestCount}</strong>
            </div>
          )}
        </div>

        {providers.length > 0 && (
          <div className="active-models">
            <div className="model-tag aff">
              <strong>Affirmative:</strong> {providers.find(p => p.id === affContext.providerId)?.model || 'Default'}
            </div>
            <div className="model-tag neg">
              <strong>Negative:</strong> {providers.find(p => p.id === negContext.providerId)?.model || 'Default'}
            </div>
            <div className="model-tag judge">
              <strong>Judge:</strong> {providers.find(p => p.id === judgeContext.providerId)?.model || 'Default'}
            </div>
          </div>
        )}
      </header>

      {/* Modal for expanded view */}
      {modalData && (
        <div className="modal-overlay" onClick={() => setModalData(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{modalData.title}</h2>
              <button className="close-btn" onClick={() => setModalData(null)}>
                <FaTimes />
              </button>
            </div>
            <div className="modal-body">
              <textarea
                value={modalData.content}
                onChange={(e) => setModalData({ ...modalData, content: e.target.value })}
                placeholder="Enter text here..."
              />
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setModalData(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => {
                modalData.onSave(modalData.content);
                setModalData(null);
              }}>Save Changes</button>
            </div>
          </div>
        </div>
      )}

      {/* Configuration */}
      <div className="config-container">
        <div className="config-group global-settings">
          <h3>⚙️ Global Settings</h3>
          <div className="config-grid">
            <div className="config-item">
              <label>Temperature: {affContext.temperature}</label>
              <input
                type="range"
                min="0"
                max="1.2"
                step="0.1"
                value={affContext.temperature}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setAffContext(prev => ({ ...prev, temperature: val }));
                  setNegContext(prev => ({ ...prev, temperature: val }));
                  setJudgeContext(prev => ({ ...prev, temperature: val }));
                }}
              />
            </div>
            <div className="config-item">
              <label>Number of Rounds:</label>
              <select value={affContext.statements.length || 3} onChange={(e) => {
                const num = parseInt(e.target.value);
                setAffContext(prev => {
                  const stmts = [...prev.statements];
                  while (stmts.length < num) stmts.push('');
                  return { ...prev, statements: stmts.slice(0, num) };
                });
                setNegContext(prev => {
                  const stmts = [...prev.statements];
                  while (stmts.length < num) stmts.push('');
                  return { ...prev, statements: stmts.slice(0, num) };
                });
              }}>
                <option value={1}>1</option>
                <option value={2}>2</option>
                <option value={3}>3</option>
              </select>
            </div>
          </div>
        </div>
        
        <div className="config-group provider-settings">
          <h3>🤖 AI Role Providers</h3>
          {providers.length > 0 ? (
            <div className="config-grid">
              <div className="config-item">
                <label>Affirmative:</label>
                <select 
                  value={affContext.providerId} 
                  onChange={(e) => handleProviderChange('affirmative', e.target.value)}
                >
                  {providers.map(p => (
                    <option key={p.id} value={p.id}>{p.model} ({p.provider})</option>
                  ))}
                </select>
              </div>
              <div className="config-item">
                <label>Negative:</label>
                <select 
                  value={negContext.providerId} 
                  onChange={(e) => handleProviderChange('negative', e.target.value)}
                >
                  {providers.map(p => (
                    <option key={p.id} value={p.id}>{p.model} ({p.provider})</option>
                  ))}
                </select>
              </div>
              <div className="config-item">
                <label>Judge:</label>
                <select 
                  value={judgeContext.providerId} 
                  onChange={(e) => handleProviderChange('referee', e.target.value)}
                >
                  {providers.map(p => (
                    <option key={p.id} value={p.id}>{p.model} ({p.provider})</option>
                  ))}
                </select>
              </div>
            </div>
          ) : (
            <div className="loading-providers">
              <FaSpinner className="spin" /> Loading providers...
            </div>
          )}
        </div>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div className="status-message">
          {statusMessage}
        </div>
      )}

      {/* Topic Input */}
      <div className="topic-section">
        <label>Debate Topic</label>
        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g., Should homework be banned in middle schools?"
          rows={3}
        />
      </div>

      {/* Generate Topics Button */}
      {/* <div className="action-section">
        <button 
          className="btn btn-primary"
          onClick={handleGenerateTopics}
          disabled={loading.topics || requestCount === null}
        >
          {loading.topics ? <FaSpinner className="spin" /> : '✨'} Generate Team Options (AI)
        </button>
      </div> */}

      {/* Team Options */}
      <div className="team-options">
        <div className="team-column affirmative">
          <div className="team-header">
            <h2>✅ Affirmative Team</h2>
            <div className="header-actions">
              <button 
                className="btn btn-sm"
                onClick={handleGenerateAffOption}
                disabled={loading.affOption || requestCount === null}
                title={requestCount === null ? "Please validate your Access Token in the header to use AI features" : ""}
              >
                {loading.affOption ? <FaSpinner className="spin" /> : <FaRobot />} AI
              </button>
            </div>
          </div>
          <div className="textarea-wrapper">
            <button 
              className="btn-expand-floating"
              onClick={() => setModalData({
                title: 'Affirmative Team Options',
                content: affContext.options,
                onSave: (val) => setAffContext(prev => ({ ...prev, options: val }))
              })}
            >
              <FaExpandAlt />
            </button>
            <textarea
              value={affContext.options}
              onChange={(e) => setAffContext(prev => ({ ...prev, options: e.target.value }))}
              placeholder="Affirmative team options (AI-generated, editable)"
              rows={8}
            />
          </div>
        </div>

        <div className="team-column negative">
          <div className="team-header">
            <h2>❌ Negative Team</h2>
            <div className="header-actions">
              <button 
                className="btn btn-sm"
                onClick={handleGenerateNegOption}
                disabled={loading.negOption || requestCount === null}
                title={requestCount === null ? "Please validate your Access Token in the header to use AI features" : ""}
              >
                {loading.negOption ? <FaSpinner className="spin" /> : <FaRobot />} AI
              </button>
            </div>
          </div>
          <div className="textarea-wrapper">
            <button 
              className="btn-expand-floating"
              onClick={() => setModalData({
                title: 'Negative Team Options',
                content: negContext.options,
                onSave: (val) => setNegContext(prev => ({ ...prev, options: val }))
              })}
            >
              <FaExpandAlt />
            </button>
            <textarea
              value={negContext.options}
              onChange={(e) => setNegContext(prev => ({ ...prev, options: e.target.value }))}
              placeholder="Negative team options (AI-generated, editable)"
              rows={8}
            />
          </div>
        </div>
      </div>

      <hr />

      {/* Rounds */}
      {affContext.statements.map((_, idx) => {
        const roundNum = idx + 1;
        const roundKey = `round${roundNum}`;
        
        return (
          <div key={roundKey} className="round-section">
            <h3>🔁 Round {roundNum}</h3>
            <div className="round-content">
              <div className="team-column affirmative">
                <div className="member-header">
                  <span>Affirmative Team</span>
                  <div className="header-actions">
                    <button 
                      className="btn btn-sm"
                      onClick={() => handleGenerateStatement(roundKey, 'aff')}
                      disabled={loading[`${roundKey}_aff`] || requestCount === null}
                      title={requestCount === null ? "Please validate your Access Token in the header to use AI features" : ""}
                    >
                      {loading[`${roundKey}_aff`] ? <FaSpinner className="spin" /> : <FaRobot />} AI
                    </button>
                  </div>
                </div>
                <div className="textarea-wrapper">
                  <button 
                    className="btn-expand-floating"
                    onClick={() => setModalData({
                      title: `Round ${roundNum} - Affirmative`,
                      content: affContext.statements[idx],
                      onSave: (val) => setAffContext(prev => {
                        const newStmts = [...prev.statements];
                        newStmts[idx] = val;
                        return { ...prev, statements: newStmts };
                      })
                    })}
                  >
                    <FaExpandAlt />
                  </button>
                  <textarea
                    value={affContext.statements[idx]}
                    onChange={(e) => setAffContext(prev => {
                      const newStmts = [...prev.statements];
                      newStmts[idx] = e.target.value;
                      return { ...prev, statements: newStmts };
                    })}
                    placeholder="Affirmative argument..."
                    rows={4}
                  />
                </div>
              </div>

              <div className="team-column negative">
                <div className="member-header">
                  <span>Negative Team</span>
                  <div className="header-actions">
                    <button 
                      className="btn btn-sm"
                      onClick={() => handleGenerateStatement(roundKey, 'neg')}
                      disabled={loading[`${roundKey}_neg`] || requestCount === null}
                      title={requestCount === null ? "Please validate your Access Token in the header to use AI features" : ""}
                    >
                      {loading[`${roundKey}_neg`] ? <FaSpinner className="spin" /> : <FaRobot />} AI
                    </button>
                  </div>
                </div>
                <div className="textarea-wrapper">
                  <button 
                    className="btn-expand-floating"
                    onClick={() => setModalData({
                      title: `Round ${roundNum} - Negative`,
                      content: negContext.statements[idx],
                      onSave: (val) => setNegContext(prev => {
                        const newStmts = [...prev.statements];
                        newStmts[idx] = val;
                        return { ...prev, statements: newStmts };
                      })
                    })}
                  >
                    <FaExpandAlt />
                  </button>
                  <textarea
                    value={negContext.statements[idx]}
                    onChange={(e) => setNegContext(prev => {
                      const newStmts = [...prev.statements];
                      newStmts[idx] = e.target.value;
                      return { ...prev, statements: newStmts };
                    })}
                    placeholder="Negative argument..."
                    rows={4}
                  />
                </div>
              </div>
            </div>
          </div>
        );
      })}

      <hr />

      {/* Final Summaries */}
      <div className="final-section">
        <h3>🧾 Final Team Summaries</h3>
        <div className="final-content">
          <div className="team-column affirmative">
            <div className="member-header">
              <span>Affirmative — Final Team Summary</span>
              <div className="header-actions">
                <button 
                  className="btn btn-sm"
                  onClick={() => handleGenerateClosing('aff')}
                  disabled={loading.closing_aff || requestCount === null}
                  title={requestCount === null ? "Please validate your Access Token in the header to use AI features" : ""}
                >
                  {loading.closing_aff ? <FaSpinner className="spin" /> : <FaRobot />} AI
                </button>
              </div>
            </div>
            <div className="textarea-wrapper">
              <button 
                className="btn-expand-floating"
                onClick={() => setModalData({
                  title: 'Affirmative Final Summary',
                  content: affContext.finalSummary,
                  onSave: (val) => setAffContext(prev => ({ ...prev, finalSummary: val }))
                })}
              >
                <FaExpandAlt />
              </button>
              <textarea
                value={affContext.finalSummary}
                onChange={(e) => setAffContext(prev => ({ ...prev, finalSummary: e.target.value }))}
                placeholder="Affirmative final summary..."
                rows={5}
              />
            </div>
          </div>

          <div className="team-column negative">
            <div className="member-header">
              <span>Negative — Final Team Summary</span>
              <div className="header-actions">
                <button 
                  className="btn btn-sm"
                  onClick={() => handleGenerateClosing('neg')}
                  disabled={loading.closing_neg || requestCount === null}
                  title={requestCount === null ? "Please validate your Access Token in the header to use AI features" : ""}
                >
                  {loading.closing_neg ? <FaSpinner className="spin" /> : <FaRobot />} AI
                </button>
              </div>
            </div>
            <div className="textarea-wrapper">
              <button 
                className="btn-expand-floating"
                onClick={() => setModalData({
                  title: 'Negative Final Summary',
                  content: negContext.finalSummary,
                  onSave: (val) => setNegContext(prev => ({ ...prev, finalSummary: val }))
                })}
              >
                <FaExpandAlt />
              </button>
              <textarea
                value={negContext.finalSummary}
                onChange={(e) => setNegContext(prev => ({ ...prev, finalSummary: e.target.value }))}
                placeholder="Negative final summary..."
                rows={5}
              />
            </div>
          </div>
        </div>
      </div>

      <hr />

      {/* Judge Button */}
      <div className="action-section">
        <button 
          className="btn btn-primary btn-large"
          onClick={handleJudge}
          disabled={loading.judge || requestCount === null}
          title={requestCount === null ? "Please validate your Access Token in the header to use AI features" : ""}
        >
          {loading.judge ? <FaSpinner className="spin" /> : <FaGavel />} Judge Winner (AI)
        </button>
      </div>

      {/* Judge Results */}
      {judgeContext.result && (
        <div className="judge-results">
          <h3>🏆 Judge Results</h3>
          
          <div className="winner-display">
            <FaTrophy className="trophy-icon" />
            <h2>{judgeContext.result.winner?.toUpperCase() || 'UNKNOWN'} TEAM WINS! 🎉</h2>
          </div>

          <div className="scores-section">
            <div className="score-box affirmative">
              <h4>✅ Affirmative Score</h4>
              <div className="score">{judgeContext.result.affirmative_score || 'N/A'}/25</div>
            </div>
            <div className="score-box negative">
              <h4>❌ Negative Score</h4>
              <div className="score">{judgeContext.result.negative_score || 'N/A'}/25</div>
            </div>
          </div>

          <div className="reasoning-section">
            <h4>📝 Judge's Reasoning</h4>
            <p>{judgeContext.result.reason || 'No reasoning provided'}</p>
          </div>

          <div className="action-section">
            <button 
              className="btn btn-secondary"
              onClick={handleDownloadTranscript}
            >
              <FaDownload /> Download Transcript
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DebateApp;
