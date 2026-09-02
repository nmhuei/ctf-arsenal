export default function BackstagePasses() {
  return (
    <main>
      <section className="panel hero">
        <h1>Backstage Access</h1>
        <p className="muted">
          Register or sign in to view your concert access card for the virtual live.
        </p>
      </section>

      <section className="forms">
        <form className="panel" method="post" action="/api/register">
          <h2>Register</h2>
          <label>
            Username
            <input name="username" minLength="3" maxLength="32" required />
          </label>
          <label>
            Password
            <input name="password" type="password" minLength="8" maxLength="128" required />
          </label>
          <button type="submit">Create Pass</button>
        </form>

        <form className="panel" method="post" action="/api/login">
          <h2>Login</h2>
          <label>
            Username
            <input name="username" minLength="3" maxLength="32" required />
          </label>
          <label>
            Password
            <input name="password" type="password" minLength="8" maxLength="128" required />
          </label>
          <button type="submit">Open Card</button>
        </form>
      </section>
    </main>
  )
}
