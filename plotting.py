import matplotlib.pyplot as plt

def plot_charts(data, lump_sum, dca, difference, crypto):
    # Plot crypto price, LS vs. DCA, and difference of returns
    plt.rcParams['figure.figsize'] = 15, 7.5
    fig, (ax1, ax2, ax3) = plt.subplots(3)

    # Plotting crypto price
    ax1.plot(data.index, data_price, color='black')
    ax1.set_title(f'{crypto} Price', size=16)
    ax1.set_ylabel('Price ($)', size=12)

    # Plotting LS vs DCA equity curves
    ax2.plot(data.index, lump_sum, color='black')
    ax2.plot(data.index, dca, color='red')
    ax2.set_title('DCA vs. Lump Sum Investing', size=16)
    ax2.set_ylabel('Current Value ($)', size=12)
    ax2.legend(['Lump Sum', 'DCA'])

    # Plotting difference between LS and DCA equity curves
    ax3.fill_between(data.index, y1=difference, y2=0, color='green', where=difference > 0, edgecolor='black')
    ax3.fill_between(data.index, y1=difference, y2=0, color='red', where=difference < 0, edgecolor='black')
    ax3.plot(data.index, difference, color='black', linewidth=.4)
    ax3.set_title('Lump Sum - DCA', size=16)
    ax3.set_ylabel('Current Value Difference ($)', size=12)
    ax3.set_xlabel('Date', size=12)
    ax3.legend(['Lump Sum > DCA', 'DCA > Lump Sum', 'Amount'])
    fig.tight_layout()
    plt.show()
