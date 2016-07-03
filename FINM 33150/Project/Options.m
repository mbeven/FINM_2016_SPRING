% Option payoff diagrams
% Michael Beven
% 20151006

%% Set Min Max S(T)

% S(T) is the stock price at maturity.  Here, we are essentially setting
% the horizontal axis of the graph.  Also, granularity is the number of 
% decimal places to which one wants to analyse the spread.  To see what's
% happening, set ST_min, ST_max and Granularity.  Then run the next section
% of code and look at ST.  

ST_min = 0; 
ST_max = 30;
Granularity = 100;

%% Generate S(T) Values

ST = linspace(ST_min,ST_max,(ST_max - ST_min)*Granularity + 1)';

%% Generate Bond

% Required Parameters

direction_B = 's'; %long or short
Num_bonds = 0;

if Num_bonds == 0
    
    payoff_B = zeros(1,(ST_max - ST_min) * Granularity + 1)';
    
else 

    B = ones(1,(ST_max - ST_min) * Granularity + 1)' * Num_bonds;

    if direction_B == 'l'
        payoff_B = B;
    else
        payoff_B = -1 * B;
    end
    
end

%% Generate Forward

% Required Parameters

direction_F = 'l'; %long or short
strike_F = 0.00;
num_forwards_F = 0;

if num_forwards_F == 0 || strike_F == 0

    payoff_F = zeros(1,(ST_max - ST_min)*Granularity + 1)';

else
    
    F = linspace(ST_min, ST_max, (ST_max - ST_min)* Granularity + 1)' ...
         *num_forwards_F ;

    if direction_F == 'l'
        payoff_F = F;
    else
        payoff_F = -1 * F;
    end

end

%% Generate Call Option 1

% Required Parameters

direction_C1 = 'l'; %long or short
strike_C1 = 15;
price_C1 = 2;
num_options_C1 = 1;

if num_options_C1 == 0

    payoff_C1 = [linspace(ST_min,ST_max,(ST_max - ST_min)*Granularity + 1)',...
        zeros(1,(ST_max - ST_min)*Granularity + 1)'];
    
else

    OTM_C1 = [linspace(ST_min,strike_C1,(strike_C1 - ST_min)*Granularity + 1)', ...
        zeros(1,(strike_C1 - ST_min)*Granularity + 1)' - price_C1*num_options_C1];

    ITM_C1 = [linspace(strike_C1 + 1/Granularity,ST_max,...
        (ST_max - strike_C1)*Granularity)', ...
        num_options_C1/Granularity*(1:(ST_max - strike_C1)*Granularity)' - ...
        price_C1*num_options_C1];

    if direction_C1 == 'l'
        payoff_C1 = [OTM_C1; ITM_C1];
    else
        payoff_C1 = -1*[OTM_C1; ITM_C1];
    end

end
%% Generate Call Option 2

% Required Parameters

direction_C2 = 's'; %long or short
strike_C2 = 20;
price_C2 = 1;
num_options_C2 = 1;

if num_options_C2 == 0
    
    payoff_C2 = [linspace(ST_min,ST_max,(ST_max - ST_min)*Granularity + 1)',...
        zeros(1,(ST_max - ST_min)*Granularity + 1)'];
    
else

    OTM_C2 = [linspace(ST_min,strike_C2,(strike_C2 - ST_min)*Granularity + 1)', ...
        zeros(1,(strike_C2 - ST_min)*Granularity + 1)' - price_C2*num_options_C2];

    ITM_C2 = [linspace(strike_C2 + 1/Granularity,ST_max,...
        (ST_max - strike_C2)*Granularity)', ...
        num_options_C2/Granularity*(1:(ST_max - strike_C2)*Granularity)' - ...
        price_C2*num_options_C2];

    if direction_C2 == 'l'
        payoff_C2 = [OTM_C2; ITM_C2];
    else
        payoff_C2 = -1*[OTM_C2; ITM_C2];
    end

end
%% Generate Put Option 1

% Required Parameters

direction_P1 = 'l'; %long or short
strike_P1 = 15;
price_P1 = 2;
num_options_P1 = 1;

if num_options_P1 == 0

    payoff_P1 = [linspace(ST_min,ST_max,(ST_max - ST_min)*Granularity + 1)',...
        zeros(1,(ST_max - ST_min)*Granularity + 1)'];

else

    ITM_P1 = [linspace(ST_min, strike_P1 - 1/Granularity,...
        (strike_P1 - ST_min)*Granularity)', ...
        num_options_P1/Granularity*(sort(1:(strike_P1 - ST_min)*Granularity,...
        'descend'))' - price_P1*num_options_P1];

    OTM_P1 = [linspace(strike_P1,ST_max,(ST_max - strike_P1)*Granularity + 1)', ...
        zeros(1,(ST_max - strike_P1)*Granularity + 1)' - price_P1*num_options_P1];

    if direction_P1 == 'l'
        payoff_P1 = [ITM_P1; OTM_P1];
    else
        payoff_P1 = -1*[ITM_P1; OTM_P1];
    end

end
%% Generate Put Option 2

% Required Parameters

direction_P2 = 's'; %long or short
strike_P2 = 10;
price_P2 = 1;
num_options_P2 = 1;

if num_options_P2 == 0

    payoff_P2 = [linspace(ST_min,ST_max,(ST_max - ST_min)*Granularity + 1)',...
        zeros(1,(ST_max - ST_min)*Granularity + 1)'];

else

    ITM_P2 = [linspace(ST_min, strike_P2 - 1/Granularity,...
        (strike_P2 - ST_min)*Granularity)', ...
        num_options_P2/Granularity*(sort(1:(strike_P2 - ST_min)*Granularity,...
        'descend'))' - price_P2*num_options_P2];

    OTM_P2 = [linspace(strike_P2,ST_max,(ST_max - strike_P2)*Granularity + 1)', ...
        zeros(1,(ST_max - strike_P2)*Granularity + 1)' - price_P2*num_options_P2];

    if direction_P2 == 'l'
        payoff_P2 = [ITM_P2; OTM_P2];
    else
        payoff_P2 = -1*[ITM_P2; OTM_P2];
    end

end
%% Build Spread

Overall_payoff = payoff_B(:) + payoff_F(:) + payoff_C1(:,2) + ...
payoff_C2(:,2) + payoff_P1(:,2) + payoff_P2(:,2);
Spread = [ST, payoff_B(:), payoff_F(:), ...
payoff_C1(:,2), payoff_C2(:,2), payoff_P1(:,2), ...
payoff_P2(:,2), Overall_payoff];
%% Plot Payoffs (note, only use Spread for this)

figure;
box on;
plot(Spread(:,1),Spread(:,4),'LineWidth',2, 'LineStyle','-',...
    'Color','Blue'); %Call 1
line(Spread(:,1),Spread(:,5),'LineWidth',1.5,'LineStyle','-.',...
    'Color','Red'); % Call 2
line(Spread(:,1),Spread(:,6),'LineWidth',2,'LineStyle','-',...
    'Color','Green'); % Put 1
line(Spread(:,1),Spread(:,7),'LineWidth',1.5,'LineStyle','-.',...
    'Color','Magenta'); % Put 2
line(Spread(:,1),Overall_payoff,'LineWidth',3,'LineStyle','--',...
    'Color','Black'); % Overall spread
hline = refline(0);
hline.Color = 'Black';
set(hline,'LineStyle','-');
axis([ST_min,ST_max,-(ST_max - ST_min)/2,(ST_max - ST_min)/2]);
set(gca,'FontSize',20);
grid on;
% Title
title('Butterfly Strategy');
% Labels
xlabel('Underlying')
ylabel('Payoff')
% Legend
legend(...
   'ATM Call K=15',...
   'Wing Call K=20',...
    'ATM Put K=15',...
    'Wing Put K=10',...
    'Overall',...
    'Location','southeast');
    

