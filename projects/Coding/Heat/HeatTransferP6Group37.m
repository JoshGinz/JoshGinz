% Define grid parameters
L = 0.3;     % Length of plate (m)
H = 0.3;     % Height of plate (m)
dx = L/49;   % Grid spacing in x-direction (m)
dy = H/49;   % Grid spacing in y-direction (m)

% Define physical parameters
k = 205;            % Thermal conductivity of aluminum (W/m-K)
rho = 2700;         % Density of aluminum (kg/m^3)
cp = 910;           % Specific heat capacity of aluminum (J/kg-K)
alpha = k/(rho*cp); % Thermal diffusivity of aluminum (m^2/s)

% Define boundary conditions
T_top = 100;             % Surface temperature at top (C)
q_left = 20000;          % Heat flux at left (W/m^2)
T_bottom = 300;          % Surface temperature at bottom (C)
h_right = 45;            % Heat transfer coefficient at right (W/m^2-K)
T_surrounding = 20;      % Surrounding temperature (C)

% Calculate additional parameters
dt = (dx^2 + dy^2)/(4*alpha); % Time step (s)
nt = 10000;                  % Number of time steps
t = 0:dt:(nt*dt);            % Time vector

% Initialize temperature matrix
T = T_surrounding*ones(50,50);
T(:,1) = T(:,1) + q_left/(k*dx);   % Left boundary
T(1,:) = T_top;                    % Top boundary
T(:,end) = (h_right*dx*T_surrounding + T(:,end-1))/(h_right*dx+ k);  % Right boundary
T(end,:) = T_bottom;               % Bottom boundary

% Define iteration matrices
Ex = alpha*dt/dx^2;
Ey = alpha*dt/dy^2;
Ax = diag(1-2*Ex*ones(1,48)) + diag(Ex*ones(1,47),1) + diag(Ex*ones(1,47),-1);
Ay = diag(1-2*Ey*ones(1,48)) + diag(Ey*ones(1,47),1) + diag(Ey*ones(1,47),-1);

% Solve PDE using iterative method
for n = 1:nt
    Tb = T;
    for i = 2:49
        Tx = Ax*T(i,2:49)';   % x-derivative of temperature
        T(i,2:49) = (Ay*Tx)'; % update temperature
    end
    T(:,1) = T(:,1) + q_left/(k*dx);   % Left boundary
    T(:,end) = (h_right*dx*T_surrounding + T(:,end-1))/(h_right*dx+ k);  % Right boundary
end

% Conduct energy balance
Q_in = q_left*L*H;                              % Heat input
Q_out = abs(k*H*(T(:,end)'-T_surrounding)/dx);  % Heat output from right boundary
Q_top = abs(-k*L*T_top/dy);                     % Heat flux from top boundary
Q_bottom = abs(-h_right*L*(T_bottom-T_surrounding)); % Heat flux from bottom boundary
Q_balance = Q_in + sum(Q_out) + Q_top + Q_bottom; % Net heat input
Q_steady = sum(Q_out) + Q_top + Q_bottom;        % Heat output at steady state

% Print results
fprintf('Heat input (W)           = %.2f\n', Q_in);
fprintf('Heat output (W)          = %.2f\n', Q_steady);
fprintf('Heat output at boundaries (W):\n');
fprintf('  Top                    = %.2f\n', Q_top);
fprintf('  Right                  = %.2f\n', Q_out(end));
fprintf('  Bottom                 = %.2f\n', Q_bottom);
fprintf('Net heat input (W)       = %.2f\n', Q_balance);
