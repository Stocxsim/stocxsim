.navbar-brand {
  padding-left: 50px;
}

.navbar .container-fluid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: nowrap;
}

/* RIGHT SIDE GROUP */
.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: nowrap;
}

.ticker-bar {
  position: sticky;

}
.dashboard_nav {
     color: black;
}

.navbar-nav {
     flex-direction: row !important;
}

.navbar-nav .nav-link {
     white-space: nowrap;
     /* prevents breaking into 2 lines */
}

/* SEARCH */
.search-box {
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  border-radius: 10px;
  background: #fff;
  max-width: 260px;
  flex: 0 1 260px;
  min-width: 0;
  overflow: hidden;
}

/* Search dropdown */
.search-results {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  /* right: 0; */
  width: 120%;
  background: rgb(231, 231, 231);
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  max-height: 220px;
  overflow-y: auto;
  display: none;
  z-index: 1000;
}
@media (max-width: 768px) {
  .search-results {
    left: auto;      /* ❌ stop left anchoring */
    right: 0;        /* ✅ anchor inward */
    width: 260px;    /* same as desktop */
  }
}
.search-item {
  padding: 10px 14px;
  cursor: pointer;
  color: #374151;
}

.search-item:hover {
  background: #f3f4f6;
}



@media (max-width: 768px) {
  .navbar .container-fluid {
    padding-left: 8px;
    padding-right: 8px;
  }

  .search-box {
    max-width: 140px;
    padding: 6px 10px;
    margin-right: 15px;
    flex-basis: 140px;
  }

  .search-box input {
    font-size: 11px;
  }

  .search-box input::placeholder {
    font-size: 11px;
    font-weight: 400;
  }

  .navbar-brand span {
    font-size: 15px;
  }

}

/* PROFILE */
.profile-wrapper {
  position: relative;
  flex-shrink: 0;
  margin-right: 30px;
  margin-left: 20px;
}

@media (max-width: 768px) {
  .profile-wrapper {
    margin-right: 5px;
    margin-left: 10px;
  }

}

.search-box input {
  border: none;
  outline: none;
  min-width: 0;
  font-size: 14px;
  width: 100%;
}

.search-icon {
  font-size: 16px;
  color: #6b7280;
}

.profile-btn {
  width: 36px;
  height: 36px;
  background: #f97316;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  cursor: pointer;

}


.profile-dropdown {
  position: absolute;
  top: 48px;
  right: 0;
  width: 320px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  display: none;
  overflow: hidden;
  z-index: 9999;
}

.profile-dropdown.show {
  display: block;
}

.profile-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-item {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f1f1;
  cursor: pointer;
}

.profile-item:hover {
  background: #f9fafb;
}

.profile-footer {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  font-weight: 500;
  cursor: pointer;
}

/* Container Styling (Hve tab-container) */
.tab-container {
  background: white;
  padding: 1px 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  gap: 40px;
  /* Tabs vacche jagya */
}
@media (max-width: 600px) {
            .tab-container {
                gap: 20px; 
                padding: 1px 10px;
            }
            .tab-item {
                font-size: 14px; 
                padding: 10px 5px;
            }
        }

/* Tab Item Styling (Hve tab-item) */
.tab-item {
  padding: 15px 5px;
  color: #7c7e8c;
  /* Inactive Text Color */
  font-weight: 500;
  font-size: 16px;
  cursor: pointer;
  position: relative;
  text-decoration: none;
  transition: color 0.2s ease;
}

/* Hover Effect */
.tab-item:hover {
  color: #44475b;
}

/* ACTIVE STATE (Jyare click thay) */
.tab-item.active {
  color: #44475b;
  /* Dark Active Text */
  font-weight: 600;
}

/* The Underline Magic */
.tab-item.active::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 3px;
  /* Thickness of underline */
  background-color: #44475b;
  /* Active Line Color */
  border-top-left-radius: 2px;
  border-top-right-radius: 2px;
} 
