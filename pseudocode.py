
  {% if validlink %}
    <h2>Change Password</h2>
    <form method="POST" class="form-group">
      {% csrf_token %}
      <br>
      <div class="form-field">
        {{ form|crispy }}
        <button type="submit" class="btn btn-primary ml-2">Change password</button>
      </div>
    </form>
  {% else %}
    <p>The password reset link was invalid, possibly because it has already been used.  Please request a new password reset.</p>
  {% endif %}

{% endblock content %}