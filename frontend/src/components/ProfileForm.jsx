export default function ProfileForm({
  form,
  onChange,
  onSubmit,
  onCancel,
  loading,
  isEdit = false,
}) {
  const fieldSections = [
    {
      title: 'Personal details',
      fields: [
        { name: 'profile_code', label: 'Profile code', type: 'text', required: true },
        { name: 'full_name', label: 'Full name', type: 'text', required: true },
        { name: 'gender', label: 'Gender', type: 'select', options: ['', 'male', 'female', 'other'] },
        { name: 'date_of_birth', label: 'Date of birth', type: 'date' },
        { name: 'age', label: 'Age', type: 'number', readOnly: true },
        { name: 'religion', label: 'Religion', type: 'text' },
        { name: 'caste', label: 'Caste', type: 'text' },
        { name: 'height_cm', label: 'Height (cm)', type: 'number', step: '0.1' },
        { name: 'weight_kg', label: 'Weight (kg)', type: 'number', step: '0.1', min: '0.1' },
        { name: 'marital_status', label: 'Marital status', type: 'text' },
        { name: 'mother_tongue', label: 'Mother tongue', type: 'text' },
        { name: 'primary_photo', label: 'Primary photo', type: 'file', accept: 'image/*' },
        { name: 'additional_photos', label: 'Additional photos', type: 'file', accept: 'image/*', multiple: true },
        { name: 'about_me', label: 'About me', type: 'textarea', fullWidth: true },
      ],
    },
    {
      title: 'Professional details',
      fields: [
        { name: 'profession', label: 'Profession', type: 'text' },
        { name: 'income_range', label: 'Income range', type: 'select', options: ['', 'BELOW_3_LPA', '3_TO_5_LPA', '5_TO_10_LPA', '10_TO_20_LPA', '20_TO_50_LPA', 'ABOVE_50_LPA', 'PREFER_NOT_TO_SAY'] },
      ],
    },
    {
      title: 'Profile review',
      fields: [
        { name: 'status', label: 'Status', type: 'select', options: ['DRAFT', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'ARCHIVED'] },
      ],
    },
  ];

  const renderInput = (field) => {
    if (field.type === 'textarea') {
      return (
        <textarea
          name={field.name}
          value={form[field.name] || ''}
          onChange={onChange}
          rows={5}
          placeholder={field.label}
        />
      );
    }

    if (field.type === 'select') {
      return (
        <select name={field.name} value={form[field.name] || ''} onChange={onChange}>
          {field.options.map((option) => {
            const optionValue = typeof option === 'string' ? option : option.value;
            const optionLabel = typeof option === 'string' ? option : option.label;
            return (
              <option key={`${field.name}-${optionValue || 'empty'}`} value={optionValue}>
                {optionLabel ? (optionValue ? optionLabel : 'Select one') : 'Select one'}
              </option>
            );
          })}
        </select>
      );
    }

    if (field.type === 'file') {
      return (
        <input
          type="file"
          name={field.name}
          accept={field.accept}
          multiple={field.multiple}
          onChange={onChange}
        />
      );
    }

    return (
      <input
        type={field.type}
        name={field.name}
        value={field.readOnly ? form[field.name] || '' : form[field.name] ?? ''}
        onChange={onChange}
        readOnly={field.readOnly}
        step={field.step}
        min={field.min}
        required={field.required}
        placeholder={field.label}
      />
    );
  };

  return (
    <section className="panel profile-form-panel">
      <div className="panel-header">
        <div>
          <div className="eyebrow">Profiles</div>
          <h2>{isEdit ? 'Edit profile' : 'Add profile'}</h2>
        </div>
        <button type="button" className="secondary-btn" onClick={onCancel} disabled={loading}>
          Cancel
        </button>
      </div>

      <form onSubmit={onSubmit} className="profile-form">
        {fieldSections.map((section) => (
          <fieldset key={section.title} className="profile-form-section">
            <legend>{section.title}</legend>
            <div className="form-grid">
              {section.fields.map((field) => (
                <div
                  key={field.name}
                  className={`form-field ${field.fullWidth ? 'full-width' : ''}`}
                >
                  <label htmlFor={field.name}>{field.label}</label>
                  {renderInput(field)}
                </div>
              ))}
            </div>
          </fieldset>
        ))}

        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : isEdit ? 'Save changes' : 'Create profile'}
          </button>
        </div>
      </form>
    </section>
  );
}
