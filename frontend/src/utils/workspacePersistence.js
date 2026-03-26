const STORAGE_PREFIX = 'nimbus.demo.workspace.v1';
const MAX_SNAPSHOTS = 12;

const EMPTY_STATE = {
  activeSessionId: null,
  sessions: [],
};

const canUseStorage = () => typeof window !== 'undefined' && Boolean(window.localStorage);

const normalizeTimestamp = (value, fallback) => {
  if (typeof value === 'string' && value.trim()) {
    return value;
  }
  return fallback;
};

const sanitizeSnapshot = (snapshot) => {
  if (!snapshot || typeof snapshot !== 'object' || typeof snapshot.sessionId !== 'string') {
    return null;
  }

  const updatedAt = normalizeTimestamp(snapshot.updatedAt, new Date().toISOString());
  const createdAt = normalizeTimestamp(snapshot.createdAt, updatedAt);

  return {
    sessionId: snapshot.sessionId,
    title: typeof snapshot.title === 'string' ? snapshot.title : '',
    objective: typeof snapshot.objective === 'string' ? snapshot.objective : 'recommendation',
    createdAt,
    updatedAt,
    chatMessages: Array.isArray(snapshot.chatMessages) ? snapshot.chatMessages : [],
    advisoryContext: snapshot.advisoryContext && typeof snapshot.advisoryContext === 'object' ? snapshot.advisoryContext : {},
    contextCoverage: snapshot.contextCoverage && typeof snapshot.contextCoverage === 'object' ? snapshot.contextCoverage : {},
    architectureOptions: Array.isArray(snapshot.architectureOptions) ? snapshot.architectureOptions : [],
    preparedSummary: typeof snapshot.preparedSummary === 'string' ? snapshot.preparedSummary : '',
    reasoningMode: typeof snapshot.reasoningMode === 'string' ? snapshot.reasoningMode : 'bedrock-model',
    allConfigs: snapshot.allConfigs && typeof snapshot.allConfigs === 'object' ? snapshot.allConfigs : {},
    schemas: snapshot.schemas && typeof snapshot.schemas === 'object' ? snapshot.schemas : {},
    serviceCatalog: snapshot.serviceCatalog && typeof snapshot.serviceCatalog === 'object' ? snapshot.serviceCatalog : {},
  };
};

const sortSnapshots = (sessions) =>
  [...sessions].sort((left, right) => new Date(right.updatedAt).getTime() - new Date(left.updatedAt).getTime());

export const createWorkspaceStorageKey = (userId) => (userId ? `${STORAGE_PREFIX}.${userId}` : null);

export const loadWorkspacePersistence = (storageKey) => {
  if (!storageKey || !canUseStorage()) {
    return EMPTY_STATE;
  }

  try {
    const rawValue = window.localStorage.getItem(storageKey);
    if (!rawValue) {
      return EMPTY_STATE;
    }

    const parsed = JSON.parse(rawValue);
    const sessions = sortSnapshots((parsed?.sessions || []).map(sanitizeSnapshot).filter(Boolean)).slice(0, MAX_SNAPSHOTS);
    const activeSessionId =
      typeof parsed?.activeSessionId === 'string' && sessions.some((session) => session.sessionId === parsed.activeSessionId)
        ? parsed.activeSessionId
        : null;

    return {
      activeSessionId,
      sessions,
    };
  } catch {
    return EMPTY_STATE;
  }
};

export const saveWorkspacePersistence = (storageKey, state) => {
  if (!storageKey || !canUseStorage()) {
    return;
  }

  const sessions = sortSnapshots((state?.sessions || []).map(sanitizeSnapshot).filter(Boolean)).slice(0, MAX_SNAPSHOTS);
  const activeSessionId =
    typeof state?.activeSessionId === 'string' && sessions.some((session) => session.sessionId === state.activeSessionId)
      ? state.activeSessionId
      : null;

  window.localStorage.setItem(
    storageKey,
    JSON.stringify({
      activeSessionId,
      sessions,
    }),
  );
};

export const upsertWorkspaceSnapshot = (sessions, snapshot) => {
  const sanitizedSnapshot = sanitizeSnapshot(snapshot);
  if (!sanitizedSnapshot) {
    return Array.isArray(sessions) ? sessions : [];
  }

  return sortSnapshots([sanitizedSnapshot, ...(Array.isArray(sessions) ? sessions : []).filter((item) => item.sessionId !== sanitizedSnapshot.sessionId)]).slice(
    0,
    MAX_SNAPSHOTS,
  );
};

export const areWorkspaceSnapshotsEqual = (left, right) => JSON.stringify(left) === JSON.stringify(right);
