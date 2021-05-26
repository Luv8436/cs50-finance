<h1>CS50 Finance</h1>
Implemented a website via which users can “buy” and “sell” stocks, a la the below.
<br><br><br>
<img src="https://cs50.harvard.edu/x/2021/psets/9/finance/finance.png" /><br><br> 
C$50 Finance, a web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values, it will also let you buy (okay, “buy”) and sell (okay, “sell”) stocks by querying IEX for stocks’ prices.

<h2>Running</h2>
Start Flask’s built-in web server (within finance/):

$ flask run

<h2>File Details</h2>
<ul>
    <li>
        application.py <br>
        <ul>
        <li>Atop the file are a bunch of imports, among them CS50’s SQL module and a few helper functions.</li>
        <li>Thereafter are a whole bunch of routes, login and logout.</li>
        <li>It uses db.execute (from CS50’s library) to query finance.db.</li>
        <li>It uses check_password_hash to compare hashes of users’ passwords.<li>Finally, login “remembers” that a user is logged in by storing his or her user_id, an INTEGER, in session. That way, any of this file’s routes can check which user, if any, is logged in. </li>
        <li>register - It allows a user to register for an account via a form.</li>
        <li>quote - It allows a user to look up a stock’s current price.</li>
        <li>buy - It enables a user to buy stocks.</li>
        <li>Index - It displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding</li>
        <li>Sell - It enables a user to sell shares of a stock (that he or she owns).</li>
        <li>History - It displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.

</li>
        </ul>
    </li>
    <li>
        helpers.py
        <ul>
            <li>There’s the implementation of apology. It renders a template, apology.html when something incorrect may happen.</li>
            <li>Thereafter is lookup, a function that, given a symbol (e.g., NFLX), returns a stock quote for a company in the form of a dict .</li>
            <li>Last in the file is usd, a short function that simply formats a float as USD.</li>
        </ul>
    </li>
</ul>