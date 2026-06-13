import re

def fix_mitigation_lab(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Update useAuditStore extraction
    content = content.replace(
        "reweighingStrength, thresholdAdjust, applyPostProcessing,",
        "reweighingMode, reweighingStrength, thresholdAdjust, applyPostProcessing,"
    )

    # Update useUploadStore extraction
    content = content.replace(
        "const { columns, targetColumn, file } = useUploadStore();",
        "const { columns, targetColumn, file, sensitiveAttributes } = useUploadStore();"
    )

    # Replace the Reweighing UI
    old_reweighing_ui = """                            <div className="space-y-4">
                                <div className="flex justify-between items-end">
                                    <label className="text-xs font-black uppercase tracking-widest text-on-surface-variant">Reweighing</label>
                                    <span className="text-sm font-black text-primary bg-primary/5 px-2 py-0.5 rounded">{Math.round((reweighingStrength || 0.5) * 100)}%</span>
                                </div>
                                <input 
                                    type="range" min="0" max="1" step="0.05" 
                                    value={reweighingStrength || 0.5} 
                                    onChange={(e) => setMitigationState({ reweighingStrength: parseFloat(e.target.value) })}
                                    className="w-full h-1.5 bg-surface-container-highest rounded-full appearance-none cursor-pointer accent-primary"
                                />
                                <p className="text-[10px] leading-relaxed text-on-surface-variant">Reweighting samples to balance group-wise representation.</p>
                            </div>"""

    new_reweighing_ui = """                            <div className="space-y-4">
                                <div className="flex justify-between items-end">
                                    <label className="text-xs font-black uppercase tracking-widest text-on-surface-variant">Reweighing</label>
                                    {sensitiveAttributes?.length > 1 && (
                                        <div className="flex bg-surface-container-highest p-1 rounded-lg">
                                            <button 
                                                onClick={() => {
                                                    setMitigationState({ 
                                                        reweighingMode: 'global',
                                                        reweighingStrength: typeof reweighingStrength === 'object' ? 0.5 : (reweighingStrength || 0.5)
                                                    });
                                                }}
                                                className={`text-[10px] font-bold px-3 py-1 rounded transition-colors ${reweighingMode === 'global' ? 'bg-white text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}
                                            >
                                                Global Weight
                                            </button>
                                            <button 
                                                onClick={() => {
                                                    const initialDict = {};
                                                    sensitiveAttributes.forEach(attr => {
                                                        initialDict[attr] = typeof reweighingStrength === 'number' ? reweighingStrength : 0.5;
                                                    });
                                                    setMitigationState({ 
                                                        reweighingMode: 'per-attribute',
                                                        reweighingStrength: initialDict
                                                    });
                                                }}
                                                className={`text-[10px] font-bold px-3 py-1 rounded transition-colors ${reweighingMode === 'per-attribute' ? 'bg-white text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}
                                            >
                                                Per-Attribute
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {reweighingMode === 'global' || !sensitiveAttributes || sensitiveAttributes.length <= 1 ? (
                                    <>
                                        <div className="flex justify-between items-end mt-2">
                                            <span className="text-[10px] font-bold text-on-surface-variant">All Attributes</span>
                                            <span className="text-sm font-black text-primary bg-primary/5 px-2 py-0.5 rounded">{Math.round(((typeof reweighingStrength === 'number' ? reweighingStrength : 0.5) || 0) * 100)}%</span>
                                        </div>
                                        <input 
                                            type="range" min="0" max="1" step="0.05" 
                                            value={typeof reweighingStrength === 'number' ? reweighingStrength : 0.5} 
                                            onChange={(e) => setMitigationState({ reweighingStrength: parseFloat(e.target.value) })}
                                            className="w-full h-1.5 bg-surface-container-highest rounded-full appearance-none cursor-pointer accent-primary"
                                        />
                                    </>
                                ) : (
                                    <div className="space-y-4 mt-2">
                                        {sensitiveAttributes.map(attr => {
                                            const val = typeof reweighingStrength === 'object' && reweighingStrength !== null && reweighingStrength[attr] !== undefined ? reweighingStrength[attr] : 0.5;
                                            return (
                                                <div key={attr} className="space-y-2 bg-primary/5 p-3 rounded-xl border border-primary/10">
                                                    <div className="flex justify-between items-end">
                                                        <span className="text-[10px] font-bold text-primary truncate max-w-[150px]">{attr}</span>
                                                        <span className="text-xs font-black text-primary bg-white px-2 py-0.5 rounded shadow-sm">{Math.round(val * 100)}%</span>
                                                    </div>
                                                    <input 
                                                        type="range" min="0" max="1" step="0.05" 
                                                        value={val} 
                                                        onChange={(e) => {
                                                            const newDict = { ...(typeof reweighingStrength === 'object' ? reweighingStrength : {}) };
                                                            newDict[attr] = parseFloat(e.target.value);
                                                            setMitigationState({ reweighingStrength: newDict });
                                                        }}
                                                        className="w-full h-1.5 bg-white rounded-full appearance-none cursor-pointer accent-primary"
                                                    />
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                                
                                <p className="text-[10px] leading-relaxed text-on-surface-variant mt-2">Reweighting samples to balance group-wise representation.</p>
                            </div>"""

    content = content.replace(old_reweighing_ui, new_reweighing_ui)

    with open(file_path, 'w') as f:
        f.write(content)

fix_mitigation_lab("/Users/kovoordheeraj/Documents/google solutions updated/fairlens-main/frontend/src/pages/MitigationLab.jsx")
fix_mitigation_lab("/Users/kovoordheeraj/Documents/google solutions updated/google_solutions-main/frontend/src/pages/MitigationLab.jsx")
print("Done")
