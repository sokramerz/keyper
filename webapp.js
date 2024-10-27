import React, { useState } from 'react';

const PasswordManager = () => {
  // Authentication states
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginStep, setLoginStep] = useState('identifier');
  const [identifier, setIdentifier] = useState('');
  const [masterPassword, setMasterPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [currentView, setCurrentView] = useState('login');
  
  // Stored passwords
  const [passwords, setPasswords] = useState([
    { id: 1, site: 'Amazon', username: 'user@example.com', password: 'SecurePass123!' },
    { id: 2, site: 'Netflix', username: 'user@example.com', password: 'NetflixPass456!' }
  ]);
  
  // New password entry
  const [newSite, setNewSite] = useState('');
  const [newUsername, setNewUsername] = useState('');

  const validateEmail = (email) => {
    return email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
  };

  const handleIdentifierSubmit = () => {
    if (!identifier || !validateEmail(identifier)) {
      setErrorMessage('Please enter a valid email address');
      return;
    }
    setLoginStep('password');
    setErrorMessage('');
  };

  const handlePasswordSubmit = () => {
    if (masterPassword.length < 8) {
      setErrorMessage('Password must be at least 8 characters');
      return;
    }
    setLoginStep('mfa');
    setErrorMessage('');
  };

  const handleMFASubmit = () => {
    if (mfaCode !== '123456') { // Demo MFA code
      setErrorMessage('Invalid MFA code');
      return;
    }
    setIsAuthenticated(true);
    setCurrentView('dashboard');
    setErrorMessage('');
  };

  const generatePassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  };

  const handleAddPassword = () => {
    if (!newSite || !newUsername) {
      setErrorMessage('Please fill in all fields');
      return;
    }
    const newPassword = generatePassword();
    setPasswords([
      ...passwords,
      {
        id: passwords.length + 1,
        site: newSite,
        username: newUsername,
        password: newPassword
      }
    ]);
    setNewSite('');
    setNewUsername('');
    setErrorMessage('');
  };

  const renderLogin = () => {
    switch (loginStep) {
      case 'identifier':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Login to Password Manager</h2>
            <input
              type="email"
              placeholder="Enter your email"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full p-2 border rounded"
            />
            <button
              onClick={handleIdentifierSubmit}
              className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Continue
            </button>
          </div>
        );

      case 'password':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Enter Master Password</h2>
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Master Password"
              value={masterPassword}
              onChange={(e) => setMasterPassword(e.target.value)}
              className="w-full p-2 border rounded"
            />
            <button
              onClick={() => setShowPassword(!showPassword)}
              className="text-blue-500"
            >
              {showPassword ? 'Hide' : 'Show'} Password
            </button>
            <button
              onClick={handlePasswordSubmit}
              className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Continue
            </button>
          </div>
        );

      case 'mfa':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Enter MFA Code</h2>
            <p className="text-sm text-gray-600">Demo code: 123456</p>
            <input
              type="text"
              placeholder="Enter 6-digit code"
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value)}
              className="w-full p-2 border rounded"
              maxLength={6}
            />
            <button
              onClick={handleMFASubmit}
              className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Verify
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Your Passwords</h2>
        <button
          onClick={() => setCurrentView('add')}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Add New
        </button>
      </div>
      
      <div className="grid gap-4">
        {passwords.map((entry) => (
          <div key={entry.id} className="p-4 border rounded">
            <h3 className="font-bold">{entry.site}</h3>
            <p className="text-gray-600">{entry.username}</p>
            <div className="flex justify-between items-center mt-2">
              <span className="font-mono">
                {showPassword ? entry.password : '••••••••••••'}
              </span>
              <button
                onClick={() => navigator.clipboard.writeText(entry.password)}
                className="text-blue-500 hover:text-blue-600"
              >
                Copy
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAddPassword = () => (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Add New Password</h2>
      <input
        type="text"
        placeholder="Website/Application"
        value={newSite}
        onChange={(e) => setNewSite(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        placeholder="Username/Email"
        value={newUsername}
        onChange={(e) => setNewUsername(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <button
        onClick={handleAddPassword}
        className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
      >
        Add Password
      </button>
      <button
        onClick={() => setCurrentView('dashboard')}
        className="w-full text-blue-500"
      >
        Back to Dashboard
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-lg">
        {errorMessage && (
          <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
            {errorMessage}
          </div>
        )}
        
        {!isAuthenticated && renderLogin()}
        {isAuthenticated && currentView === 'dashboard' && renderDashboard()}
        {isAuthenticated && currentView === 'add' && renderAddPassword()}
      </div>
    </div>
  );
};

export default PasswordManager;
