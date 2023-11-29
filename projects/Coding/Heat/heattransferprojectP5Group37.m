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
nt = 1000;                  % Number of time steps
t = 0:dt:(nt*dt);            % Time vector

% Define initial conditions
T = ones(50, 50)*T_surrounding;

% Set temperature of center node
T(25, 25) = (T(25, 24) + T(25, 26) + T(24, 25) + T(26, 25))/4;

% Set boundary conditions
T(1, :) = T_top;
T(2:end-1, 1) = (T(2:end-1, 2) + q_left*dy/k)/(1+2*dy/k); % Left surface nodes
T(end, :) = T_bottom;
T(2:end-1, end) = (T(2:end-1, end-1) + h_right*dy*T_surrounding/k)/(1+2*h_right*dy/k); % Right surface nodes


% Loop through time steps
for i = 1:nt
    % Update inner grid points using explicit finite difference method
    for j = 2:49
        for k = 2:49
            if j == 25 && k == 25 % omit the center node from the heat equation
                continue
            end
            T(k,j) = T(k,j) + alpha*dt/(dx^2)*...
                (T(k,j+1) - 2*T(k,j) + T(k,j-1)) +...
                alpha*dt/(dy^2)*(T(k+1,j) - 2*T(k,j) + T(k-1,j));
        end
    end
    
    % Update temperature of center node separately
    T(25, 25) = (T(25, 24) + T(25, 26) + T(24, 25) + T(26, 25))/4;

    % Set boundary conditions for each time step
    T(1, :) = T_top;
    T(2:end-1, 1) = (T(2:end-1, 2) + q_left*dy/k)/(1+2*dy/k); % Left surface nodes
    T(end, :) = T_bottom;
    T(2:end-1, end) = (T(2:end-1, end-1) + h_right*dy*T_surrounding/k)/(1+2*h_right*dy/k); % Right surface nodes
    
    % Plot temperature distribution at certain time steps
    if mod(i, 1000) == 0
        [X,Y] = meshgrid(0:dx:L,0:dy:H);
        I = surf(X,Y,T')
        xlabel('Length (m)')
        ylabel('Height (m)')
        zlabel('Temperature (C)')
        title(sprintf('Temperature Distribution at Time = %0.2f s', t(i)))
        colorbar
        view([90 -270])
        drawnow
        set(I, 'EdgeColor', 'none')

    end
end


